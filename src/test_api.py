import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv(encoding="utf-8-sig")
API_KEY = os.getenv("HENRIK_API_KEY")
print("Cle lue :", (API_KEY[:8] + "...") if API_KEY else "RIEN")

NAME = "Yu Otosaka"
TAG = "OEGR"

url = f"https://api.henrikdev.xyz/valorant/v1/account/{quote(NAME)}/{quote(TAG)}"
r = requests.get(url, headers={"Authorization": API_KEY})

print("Statut :", r.status_code)
print(r.json())