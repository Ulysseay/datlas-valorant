import json
import os
import time
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv(encoding="utf-8-sig")
API_KEY = os.getenv("HENRIK_API_KEY")

NAME = "Yu Otosaka"
TAG = "OEGR"
REGION = "eu"

BASE = "https://api.henrikdev.xyz"
HEADERS = {"Authorization": API_KEY}

all_matches = []
page = 1

while True:
    url = f"{BASE}/valorant/v1/stored-matches/{REGION}/{quote(NAME)}/{quote(TAG)}"
    params = {"mode": "competitive", "page": page, "size": 25}
    r = requests.get(url, headers=HEADERS, params=params)

    if r.status_code == 429:
        print("Rate limit atteint - pause de 65 s puis on reprend...")
        time.sleep(65)
        continue

    if r.status_code != 200:
        print(f"Arret : statut {r.status_code} - {r.text[:200]}")
        break

    payload = r.json()
    batch = payload.get("data", [])
    if not batch:
        print("Plus de donnees - historique complet recupere.")
        break

    all_matches.extend(batch)
    total = payload.get("results", {}).get("total", "?")
    print(f"Page {page} : +{len(batch)} matchs (cumul {len(all_matches)} / total serveur {total})")

    page += 1
    time.sleep(2.1)

os.makedirs("data/raw", exist_ok=True)
with open("data/raw/stored_matches.json", "w", encoding="utf-8") as f:
    json.dump(all_matches, f, ensure_ascii=False, indent=2)

print(f"OK - {len(all_matches)} matchs sauvegardes dans data/raw/stored_matches.json")