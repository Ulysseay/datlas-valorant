import json
import os

import pandas as pd

RAW_PATH = "data/raw/stored_matches.json"
OUT_PATH = "data/clean/matches.csv"
SESSION_GAP_MINUTES = 90


def parse_match(m):
    meta = m["meta"]
    stats = m["stats"]
    teams = m["teams"]

    my_team = str(stats.get("team", "")).lower()
    rounds_red = teams.get("red")
    rounds_blue = teams.get("blue")
    if my_team == "red":
        rw, rl = rounds_red, rounds_blue
    elif my_team == "blue":
        rw, rl = rounds_blue, rounds_red
    else:
        rw, rl = None, None

    shots = stats.get("shots") or {}
    head = shots.get("head") or 0
    body = shots.get("body") or 0
    leg = shots.get("leg") or 0
    total_shots = head + body + leg

    damage = stats.get("damage") or {}
    character = stats.get("character") or {}

    return {
        "match_id": meta.get("id"),
        "date": meta.get("started_at"),
        "map": (meta.get("map") or {}).get("name"),
        "mode": meta.get("mode"),
        "season": (meta.get("season") or {}).get("short"),
        "agent": character.get("name"),
        "team": my_team,
        "tier": stats.get("tier"),
        "rounds_won": rw,
        "rounds_lost": rl,
        "kills": stats.get("kills", 0),
        "deaths": stats.get("deaths", 0),
        "assists": stats.get("assists", 0),
        "score": stats.get("score", 0),
        "hs_pct": round(100 * head / total_shots, 1) if total_shots else None,
        "dmg_made": damage.get("made"),
        "dmg_received": damage.get("received"),
    }


def main():
    with open(RAW_PATH, encoding="utf-8") as f:
        raw = json.load(f)

    rows = []
    skipped = 0
    for m in raw:
        try:
            rows.append(parse_match(m))
        except (KeyError, TypeError):
            skipped += 1

    df = pd.DataFrame(rows)

    # Types & filtres
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df = df.dropna(subset=["date", "rounds_won", "rounds_lost"])
    df["date"] = df["date"].dt.tz_convert("Europe/Paris")
    df = df[df["mode"].str.lower().str.contains("competitive", na=False)]

    # Cible ML : win (egalites exclues)
    df = df[df["rounds_won"] != df["rounds_lost"]].copy()
    df["win"] = (df["rounds_won"] > df["rounds_lost"]).astype(int)

    # Features derivees
    df = df.sort_values("date").reset_index(drop=True)
    df["kd"] = (df["kills"] / df["deaths"].clip(lower=1)).round(2)
    df["hour"] = df["date"].dt.hour
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    df["weekday"] = df["date"].dt.dayofweek.map(dict(enumerate(jours)))

    # Sessions (le Tilt Detector se nourrit ici)
    gap = df["date"].diff().dt.total_seconds().div(60)
    df["session_id"] = (gap > SESSION_GAP_MINUTES).cumsum()
    df["match_in_session"] = df.groupby("session_id").cumcount() + 1

    os.makedirs("data/clean", exist_ok=True)
    df.to_csv(OUT_PATH, index=False)

    print(f"OK - {len(df)} matchs propres -> {OUT_PATH}")
    if skipped:
        print(f"({skipped} matchs ignores car incomplets)")
    print(f"Winrate global : {df['win'].mean():.1%}")
    print(f"Periode : {df['date'].min():%d/%m/%Y} -> {df['date'].max():%d/%m/%Y}")
    print(f"Agents joues : {df['agent'].nunique()} | Maps : {df['map'].nunique()} | Sessions : {df['session_id'].nunique()}")
if __name__ == "__main__":
    main()   