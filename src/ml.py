import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

df = pd.read_csv("data/clean/matches.csv")

# =========================================================
# MODELE A - EXPLICATIF (stats in-game -> associations)
# Question : quels facteurs sont ASSOCIES a mes victoires ?
# =========================================================
feats_a = ["kills", "deaths", "assists", "kd", "hs_pct", "match_in_session", "hour"]
dfa = df.dropna(subset=feats_a)
Xa, ya = dfa[feats_a], dfa["win"]

rf = RandomForestClassifier(n_estimators=300, random_state=42)
score_a = cross_val_score(rf, Xa, ya, cv=5).mean()
rf.fit(Xa, ya)

imp = (
    pd.DataFrame({"feature": feats_a, "importance": rf.feature_importances_})
    .sort_values("importance", ascending=False)
)
imp.to_csv("data/clean/feature_importance.csv", index=False)

print("=== MODELE A - explicatif ===")
print(f"Accuracy (validation croisee) : {score_a:.1%}")
print(imp.to_string(index=False))
top = imp.iloc[0]
print(f"\nInsight : le facteur n1 associe a mes victoires est << {top['feature']} >>.")

# =========================================================
# MODELE B - PREDICTIF HONNETE (features connues AVANT le match)
# Question : peut-on predire l'issue avant de lancer ? (pas de leakage)
# =========================================================
num_b = ["match_in_session", "hour"]
cat_b = ["agent", "map", "weekday"]
dfb = df.dropna(subset=num_b + cat_b)
Xb, yb = dfb[num_b + cat_b], dfb["win"]

pre = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), cat_b)],
    remainder="passthrough",
)

logreg = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
score_b = cross_val_score(logreg, Xb, yb, cv=5).mean()
baseline = max(yb.mean(), 1 - yb.mean())

print("\n=== MODELE B - predictif honnete (pre-match) ===")
print(f"Accuracy : {score_b:.1%} | Baseline (toujours predire la classe majoritaire) : {baseline:.1%}")
if score_b <= baseline + 0.02:
    print("Verdict honnete : l'issue d'un match est quasi imprevisible avant de le lancer -")
    print("ce qui compte se joue PENDANT le match. C'est un vrai resultat, publiable tel quel.")
else:
    print("Verdict : certaines conditions pre-match (agent, heure, fatigue) pesent reellement sur mes chances.")