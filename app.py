import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Datlas × Valorant", page_icon="🎯", layout="wide")

ROUGE = "#FF4655"
BLEU = "#53DDF0"


@st.cache_data
def load_data():
    df = pd.read_csv("data/clean/matches.csv")
    df["date"] = pd.to_datetime(df["date"], utc=True).dt.tz_convert("Europe/Paris")
    return df


df = load_data()

# ---------- Header ----------
st.title("Datlas × Valorant")
st.caption("4 ans de ranked analysés comme un Product Analyst — la question : qu'est-ce qui me fait vraiment gagner ?")

# ---------- Filtres ----------
with st.sidebar:
    st.header("Filtres")
    agents = st.multiselect("Agents", sorted(df["agent"].dropna().unique()))
    maps = st.multiselect("Maps", sorted(df["map"].dropna().unique()))

f = df.copy()
if agents:
    f = f[f["agent"].isin(agents)]
if maps:
    f = f[f["map"].isin(maps)]

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Matchs analysés", len(f))
c2.metric("Winrate", f"{f['win'].mean():.1%}" if len(f) else "—")
c3.metric("K/D moyen", f"{f['kd'].mean():.2f}" if len(f) else "—")
agent_sig = f["agent"].mode().iloc[0] if len(f) else "—"
c4.metric("Agent signature", agent_sig)

st.divider()

# ---------- Onglets = les hypothèses de l'enquête ----------
tab1, tab2, tab3, tab4 = st.tabs(
    ["📈 Vue d'ensemble", "🎭 Agents & Maps", "🧠 Rythme & Tilt", "🔬 Le labo IA"]
)

with tab1:
    monthly = (
        f.set_index("date")
        .resample("ME")["win"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "winrate", "count": "matchs"})
    )
    fig = px.line(
        monthly, x="date", y="winrate", markers=True,
        title="Winrate mensuel", color_discrete_sequence=[ROUGE],
    )
    fig.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig, width="stretch")

with tab2:
    col_a, col_b = st.columns(2)
    by_agent = f.groupby("agent").agg(winrate=("win", "mean"), matchs=("win", "size")).reset_index()
    by_agent = by_agent[by_agent["matchs"] >= 10].sort_values("winrate")
    fig_a = px.bar(
        by_agent, x="winrate", y="agent", orientation="h",
        title="Winrate par agent (≥ 10 matchs)", color_discrete_sequence=[ROUGE],
    )
    fig_a.update_xaxes(tickformat=".0%")
    col_a.plotly_chart(fig_a, width="stretch")

    by_map = f.groupby("map").agg(winrate=("win", "mean"), matchs=("win", "size")).reset_index()
    by_map = by_map[by_map["matchs"] >= 10].sort_values("winrate")
    fig_m = px.bar(
        by_map, x="winrate", y="map", orientation="h",
        title="Winrate par map (≥ 10 matchs)", color_discrete_sequence=[BLEU],
    )
    fig_m.update_xaxes(tickformat=".0%")
    col_b.plotly_chart(fig_m, width="stretch")

with tab3:
    st.subheader("Le Tilt Detector")
    st.caption("Hypothèse : « je perds quand j'enchaîne ». Winrate selon la position du match dans la session (pause > 90 min = nouvelle session).")
    tilt = (
        f.groupby("match_in_session")
        .agg(winrate=("win", "mean"), matchs=("win", "size"))
        .reset_index()
    )
    tilt = tilt[tilt["matchs"] >= 15]
    fig_t = px.bar(
        tilt, x="match_in_session", y="winrate",
        title="Winrate selon le n° du match dans la session",
        color_discrete_sequence=[ROUGE],
    )
    fig_t.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_t, width="stretch")

    by_hour = f.groupby("hour").agg(winrate=("win", "mean"), matchs=("win", "size")).reset_index()
    by_hour = by_hour[by_hour["matchs"] >= 10]
    fig_h = px.bar(
        by_hour, x="hour", y="winrate",
        title="Winrate selon l'heure de la journée", color_discrete_sequence=[BLEU],
    )
    fig_h.update_yaxes(tickformat=".0%")
    st.plotly_chart(fig_h, width="stretch")

with tab4:
    st.subheader("Qu'est-ce qui me fait vraiment gagner ?")
    st.caption("Deux modèles : un explicatif (stats in-game → associations) et un prédictif honnête (features connues AVANT le match — pas de data leakage).")
    LABELS = {
        "kd": "Ratio K/D (efficacité kills/morts)",
        "deaths": "Nombre de morts",
        "hs_pct": "% de tirs à la tête (précision)",
        "kills": "Nombre de kills",
        "assists": "Nombre d'assists",
        "hour": "Heure de la journée",
        "match_in_session": "Fatigue (n° du match dans la session)",
    }
    try:
        imp = pd.read_csv("data/clean/feature_importance.csv")
        imp["feature"] = imp["feature"].map(LABELS).fillna(imp["feature"])
        imp["importance"] = imp["importance"] * 100
        fig_i = px.bar(
            imp.sort_values("importance"),
            x="importance", y="feature", orientation="h",
            title="Poids de chaque facteur dans mes victoires (modèle explicatif — total = 100 %)",
            color_discrete_sequence=[ROUGE],
            text=imp.sort_values("importance")["importance"].map(lambda v: f"{v:.1f} %"),
        )
        fig_i.update_traces(textposition="outside")
        fig_i.update_xaxes(title="Importance (%)", ticksuffix=" %")
        fig_i.update_yaxes(title="")
        st.plotly_chart(fig_i, width="stretch")
        st.caption(
            "Lecture : le modèle (Random Forest, accuracy 72,6 % en validation croisée) mesure la part de chaque facteur "
            "dans la distinction victoire/défaite. Insight clé : le ratio K/D et les morts pèsent plus que les kills — "
            "**survivre compte davantage que fragger**. Association ≠ causalité."
        )
    except FileNotFoundError:
        st.info("La couche IA arrive en v2 — lance src/ml.py pour générer les résultats.")

st.divider()
st.caption("Projet Datlas — données : API HenrikDev (non affiliée à Riot Games). Seules mes propres statistiques sont conservées et publiées.")