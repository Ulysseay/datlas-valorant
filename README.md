# 🎯 Datlas × Valorant — 4 ans de ranked analysés comme un Product Analyst

**[▶️ Dashboard live](https://datlas-valorant.streamlit.app)** · Épisode 2 de la série [Datlas](https://datlas-ulysse.streamlit.app)

## La question
Après 5 ans de Valorant (pic : Radiant) et **1 142 matchs compétitifs** analysés : **qu'est-ce qui me fait vraiment gagner ?**
Trois hypothèses testées : « je gagne parce que je frag » · « je perds quand j'enchaîne » · « j'ai des maps à bannir ».

## 3 découvertes
1. **Le tilt est mesurable.** Mon winrate passe de 52 % au 2ᵉ match d'une session à 40 % au 5ᵉ match enchaîné — **−12 points**. (La remontée apparente au 6ᵉ est un biais de survie : on ne prolonge que les bons soirs.)
2. **Survivre > fragger.** Mes morts pèsent **1,7× plus** que mes kills dans mes victoires (21,5 % vs 12,5 % d'importance). Le facteur n°1 : le ratio K/D (23,6 %) — l'efficacité, pas le volume.
3. **Avant de lancer, l'issue est imprévisible.** Le modèle « pré-match » (agent, map, heure, fatigue) fait 48,9 % — sous la baseline (51,3 %). Pas de map maudite ni d'heure magique : tout se joue pendant le match.

## Pourquoi DEUX modèles (le choix méthodo dont je suis le plus fier)
Prédire une victoire avec les kills du match serait du **data leakage** : les kills arrivent *pendant* le match.
- **Modèle A — explicatif** (Random Forest, 72,6 % en validation croisée) : stats in-game → facteurs *associés* aux victoires.
- **Modèle B — prédictif honnête** (régression logistique) : uniquement ce qui est connu *avant* le match. Son échec à battre la baseline est un résultat, pas un bug.

## Stack & pipeline
`API HenrikDev → Python (requests) → nettoyage & features (pandas) → dashboard (Streamlit + Plotly) → ML (scikit-learn) → Streamlit Cloud`

1 167 matchs récupérés (pagination + rate limiting) · 1 142 conservés après nettoyage · 658 sessions reconstruites (pause > 90 min = nouvelle session) · période : mai 2022 → juillet 2026.

## Éthique des données
Les données brutes contiennent les pseudos de 9 autres joueurs par match : le pipeline ne conserve et ne publie **que mes propres statistiques**.

## Lancer en local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Limites connues
- L'historique couvre les matchs stockés par l'API (4 ans), pas l'intégralité de mes 5 ans de jeu.
- Association ≠ causalité : le modèle A décrit, il ne prouve pas.
- v2 envisagée : détail par round (endpoint match v4), comparaison à la meta pro.

---
*[Ulysse Ayivi](https://www.linkedin.com/in/ulysseayivi/) — Data Analyst · Python, SQL, Power BI. Données : API HenrikDev, non affiliée à Riot Games.*