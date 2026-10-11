# WattIf — Consommation électrique quotidienne en France : prévision à 7 jours, contrefactuels COVID et sobriété

Mini-projet de séries temporelles (Tek-Up, 3e année ingénieur Data Science et IA).

## Présentation

Le projet étudie la consommation électrique quotidienne de la France (RTE éCO2mix, 3 896 jours du 1er janvier 2016 au 31 août 2026) avec la température moyenne nationale (ODRÉ). Il poursuit deux objectifs :

1. **prévoir** la consommation à sept jours et comparer dix modèles sur un protocole commun (SARIMA, VAR, VECM, AR-GARCH, Prophet, LSTM, GRU, hybride SARIMA + LSTM, deux références naïves) ;
2. **mesurer** l'effet du premier confinement de 2020 et de la sobriété de 2022-2025 par une analyse contrefactuelle.

Le découpage est chronologique : **90 % d'apprentissage (3 506 jours, jusqu'au 6 août 2025) et 10 % de test (390 jours, du 7 août 2025 au 31 août 2026)**.

**Résultat principal.** Sur le test (390 jours), AR-GARCH(1,2)-t a la plus petite erreur (RMSE 74,45 GWh/jour), mais aucun test de Diebold–Mariano corrigé (Holm) ne le distingue de SARIMA, LSTM, GRU, VAR(3) ni de l'hybride. SARIMA(2,1,1)(0,1,1)[7] est le modèle retenu par la règle de validation interne ; AR-GARCH est le meilleur observé sur le test, à égalité avec le GRU en validation croisée ; nous ne concluons pas à une supériorité durable. Le témoin « AR à variance constante » obtient une RMSE de 74,06 GWh/jour.

Le rapport complet est dans `rapport/rapport_final.pdf` (et `rapport/rapport_final.docx`).

## Auteurs

| Auteur(e) | Parties | Fichiers principaux |
|---|---|---|
| Fayfa | Données, analyse exploratoire, contrefactuels, visualisations | `01_preparation_donnees.ipynb`, `02_eda.ipynb`, `03_contrefactuels.ipynb`, `04_visualisations.ipynb` |
| Yosra | ARIMA/SARIMA, IA générative et LLM | `arima_sarima.ipynb`, `rapport/annexe_llm/` |
| Ghada | VAR, Granger, VECM, GARCH, Prophet | `05_var_vecm_garch_prophet.ipynb` |
| Anwar | Socle classique en R, corrélation glissante | `06_section3_R.ipynb` |
| Anas | LSTM, GRU, hybride, comparaison finale | `07_lstm_gru.ipynb` |

## Structure des dossiers

| Chemin | Contenu |
|---|---|
| `data/daily.csv` | jeu de données préparé (une ligne par jour, cible `conso_gwh`) |
| `01_…` à `07_…`, `arima_sarima.ipynb` | les huit notebooks (sept en Python, un en R) |
| `scripts/` | scripts d'exécution, de mesure et d'assemblage du rapport |
| `exports/` | tableaux de résultats (`exports/ghada/`, `exports/R/`, `exports/lstm_gru/`) |
| `forecasts/` | prévisions du test (390 jours) de chaque modèle |
| `figures/` | graphiques |
| `rapport/` | sections du rapport, `rapport_final.*`, annexe LLM (`rapport/annexe_llm/`) |
| `tests/` | tests automatiques du protocole de prévision et des tests statistiques |
| `requirements.txt`, `R_packages.txt` | dépendances Python épinglées, paquets R |

## Installation

Python 3.11 :

```sh
python -m venv .venv
source .venv/bin/activate            # Windows : .\.venv\Scripts\activate
python -m pip install -r requirements.txt
```

R 4.5.2, pour le notebook `06_section3_R.ipynb` (voir `R_packages.txt`) :

```r
install.packages(c("forecast", "tseries", "urca", "tsibble", "vars", "rugarch", "uroot", "zoo", "sandwich", "lmtest", "IRdisplay", "IRkernel"))
IRkernel::installspec()
```

## Ordre d'exécution des notebooks

Tous les notebooks se lancent depuis la racine du projet et s'exécutent de haut en bas.

| Ordre | Notebook | Langage | Rôle | Dépend de |
|---|---|---|---|---|
| 1 | `01_preparation_donnees.ipynb` | Python | construit `data/daily.csv` | `data/raw/` (voir ci-dessous) |
| 2 | `02_eda.ipynb` | Python | analyse exploratoire (section 2) | `data/daily.csv` |
| 3 | `03_contrefactuels.ipynb` | Python | contrefactuels (section 7.2) | `data/daily.csv` |
| 4 | `04_visualisations.ipynb` | Python | spirale et carpet plot | `data/daily.csv` |
| 5 | `arima_sarima.ipynb` | Python | ARIMA et SARIMA (section 3.1) | `data/daily.csv`, `scripts/finalisation.py` |
| 6 | `05_var_vecm_garch_prophet.ipynb` | Python | VAR, VECM, GARCH, Prophet (sections 3.2, 3.3, 4.3) | notebook `arima_sarima` |
| 7 | `06_section3_R.ipynb` | R | socle classique en R (section 3.4) et corrélation glissante (section 7.1) | notebooks `arima_sarima` et 05 |
| 8 | `07_lstm_gru.ipynb` | Python | LSTM, GRU, hybride, comparaison et tests (sections 4.1, 4.2, 6) | notebooks `arima_sarima` et 05 |

**Données brutes.** Les fichiers sources (`data/raw/`) ne sont pas fournis, en raison de leur taille. La première cellule de code du notebook 01 détecte leur absence, affiche les adresses de téléchargement (ODRÉ : `eco2mix-national-cons-def` et `temperature-quotidienne-regionale`) et s'arrête ; les autres notebooks utilisent `data/daily.csv`, qui est fourni.

Calculs complémentaires du rapport (après les notebooks) :

```sh
python scripts/stats_descriptives.py     # statistiques descriptives (section 5)
python scripts/garch_volatilite.py       # volatilité conditionnelle et événements (section 3.3)
python scripts/courbes_perte.py          # courbes de perte train/validation (section 4.1)
python scripts/cv_temporelle.py          # validation croisée temporelle, environ 9 minutes sur CPU (section 4.1)
python scripts/cv_ar_garch.py            # validation croisée d'AR-GARCH et du témoin AR sur les mêmes plis, quelques secondes (annexe A)
python scripts/mesures_complexite.py     # nombre de paramètres et temps d'ajustement (section 6)
python scripts/preparer_prompts_llm.py   # prompts de la section 5
python scripts/audit_reponses_llm.py     # vérifications chiffrées de l'audit des réponses du LLM (section 5.6)
python scripts/generer_annexes.py        # tableaux de l'annexe A
python scripts/assembler_rapport.py      # rapport_final.md, .docx et .pdf (pandoc et Edge ou Chrome requis)
python -m unittest discover -s tests -v  # tests automatiques
python scripts/verifier_livrables.py     # contrôles de cohérence des exports
```

## Reproductibilité

- **Graines.** Python : `numpy.random.seed(42)` (notebooks 01 et 02), `SEED = 42` (notebook 05, tirages de Prophet), graines 42 à 46 pour les cinq réseaux de chaque modèle (notebook 07, `torch.manual_seed`, calcul déterministe sur un seul fil). R : `set.seed(42)` (notebook 06). Les scripts de `scripts/` utilisent les mêmes graines.
- **Versions.** `requirements.txt` épingle l'environnement Python 3.11 dans lequel les scripts, les tests et les calculs complémentaires ont été exécutés. Les sorties enregistrées dans les notebooks proviennent de plusieurs environnements, dont les versions sont affichées dans les notebooks (Python 3.13.5 avec pandas 2.2.3 pour les notebooks 01 à 04 ; numpy 1.26.4, pandas 2.3.3, statsmodels 0.14.6 et pmdarima 2.0.4 pour `arima_sarima` ; Python 3.11.5, pandas 3.0.6, arch 8.0.0 et prophet 1.5.0 pour le notebook 05 ; R 4.5.2 pour le notebook 06 ; Python 3.10.8 et PyTorch 2.12.0 pour le notebook 07). Selon les versions des paquets, de petits écarts numériques (inférieurs à 0,01 sur les métriques du modèle retenu) sont possibles à la réexécution.
- **Contraintes de versions.** `pmdarima 2.0.4` (recherche `auto_arima`, notebooks 02 et `arima_sarima`) impose `numpy < 2` et `scikit-learn == 1.6.1` : avec scikit-learn 1.9.1, il échoue avec `TypeError: check_array() got an unexpected keyword argument 'force_all_finite'`. Le notebook 07 demande `pandas < 3`. `requirements.txt` épingle donc `numpy==1.26.4`, `pandas==2.3.3` et `scikit-learn==1.6.1`.
- **Chemins.** Tous les chemins sont relatifs à la racine du projet.

## Limites principales

Un seul hiver de test, validation interne courte et estivale, aucune météo future, protocoles légèrement différents selon les modèles (Prophet réajusté chaque semaine, hybride pseudo hors échantillon, tests de Diebold–Mariano sur 385 jours contre 390 pour les métriques), diagnostics résiduels défavorables pour tous les modèles statistiques. Le détail figure dans les sections 8 et 9 du rapport.
