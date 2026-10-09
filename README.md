# WattIf — Séries temporelles de consommation électrique

Projet de groupe : préparation des données, analyse exploratoire, contrefactuels et prévisions ARIMA/SARIMA.

## Fichiers

| Chemin | Contenu |
|---|---|
| `01_preparation_donnees.ipynb` | Préparation de Fayfa |
| `02_eda.ipynb` | Analyse exploratoire, ACF/PACF, ADF/KPSS |
| `03_contrefactuels.ipynb` | Analyse contrefactuelle fournie |
| `04_visualisations.ipynb` | Visualisations fournies |
| `arima_sarima.ipynb` | Modèles exécutés, validation interne et diagnostics ; choix final à poursuivre |
| `data/daily.csv` | Données quotidiennes préparées |
| `figures/` | Figures et tableaux fournis par Fayfa |
| `docs/` | État du projet, provenance et sauvegarde du notebook |

## Démarrer

Ouvrir ce dossier dans VS Code ou lancer Jupyter depuis sa racine. Dans un terminal :

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyter lab
```

Choisir le noyau Python de `.venv`. Commencer par lire `02_eda.ipynb`, puis `arima_sarima.ipynb`. Les sorties de Fayfa sont conservées ; elles n'ont pas été recalculées lors de l'intégration.

`data/daily.csv` permet de démarrer sans refaire la préparation. Les fichiers sources `data/raw/` ne sont pas fournis dans le ZIP : le notebook 01 ne peut donc pas être réexécuté intégralement en l'état. Les autres notebooks peuvent nécessiter leurs dépendances et leurs fichiers d'entrée ; l'intégration ne vaut pas validation de leur exécution.

## Données et protocole

3 896 observations quotidiennes, du 1er janvier 2016 au 31 août 2026. Cible : `conso_gwh`, en GWh/jour. Le fichier comprend aussi températures, production, calendrier et indicateur d'interpolation des températures.

Découpage de Fayfa : 3 506 jours d'entraînement jusqu'au 6 août 2025 ; 390 jours de test à partir du 7 août 2025. Le notebook ARIMA conserve ce test externe et réserve les 56 derniers jours de l’apprentissage à huit validations successives de 7 jours. L'horizon de prévision demandé est de 7 jours ; il est distinct de la longueur du test.

## Collaboration GitHub

Ce dossier est préparé pour être partagé, mais aucun dépôt distant n'a été créé ni publié. Avant de publier, vérifier les droits de partage des données et les sorties des notebooks. Éviter de modifier simultanément le même notebook ; chacun peut travailler sur sa branche puis proposer ses changements.

Les dépendances ne sont pas figées : après une exécution complète réussie, enregistrer les versions utilisées. Voir `docs/etat_du_projet.md` pour le travail restant.

## Reproduire la comparaison ARIMA

L'environnement local `.venv` a été préparé pour Python 3.9. Les versions installées sont consignées dans `requirements-lock.txt` (environnement macOS de cette exécution). Pour lancer uniquement la préparation, les modèles, la validation interne et les diagnostics depuis la racine :

```sh
.venv/bin/python scripts/executer_comparaison.py
```

Le script enregistre les sorties dans le notebook et les tableaux dans `exports/`. Il s'arrête avant la sélection finale et n'évalue pas le test externe. Fermer ou recharger le notebook dans l'éditeur pour éviter d'écraser ces sorties avec une ancienne version ouverte.

Pour Python 3.9, le projet utilise pmdarima 2.0.4 et NumPy < 2 ; la prise en charge de NumPy 2 est arrivée dans pmdarima 2.1, qui abandonne Python 3.9 ([notes de version officielles](https://github.com/alkaline-ml/pmdarima/releases)).

Premiers résultats : voir [la comparaison commentée](docs/resultats_premiere_comparaison.md). Les modèles restent provisoires car les diagnostics résiduels sont défavorables.
# projet-series-temporelles
