# WattIf — consommation électrique et prévisions

**La partie ARIMA/SARIMA est exécutée jusqu'aux prévisions finales.** Le projet conserve les données, notebooks et figures de Fayfa, puis ajoute la modélisation et les livrables de la partie prévision.

## Commencer ici

- [Notebook exécuté](arima_sarima.ipynb) : explications, modèles, validation, diagnostics, test externe et prévisions.
- [Section 3.1 du rapport](rapport/section_3_1_arima_sarima.md) : méthode et résultats chiffrés.
- [Section 5 du rapport](rapport/section_5_analyse_llm.md) : vulgarisation, recommandations et audit critique.
- [Annexe LLM](rapport/annexe_llm/README.md) : prompts et réponses intégrales, avec provenance déclarée.
- [Livraison pour Anas](livraison_anas/README.md) et `livraison_anas.zip` : fichiers à transmettre manuellement.
- [État des tâches](docs/etat_du_projet.md) et [vérifications](docs/verification_finale.md).

**Point personnel restant :** l'étudiante a confirmé ne pas avoir rédigé d'analyse avant l'aide IA. Cette condition du sujet ne peut pas être satisfaite rétroactivement. Les textes fournis sont déclarés comme assistés. Une [réflexion personnelle après assistance](rapport/reflexion_personnelle_a_rediger.md) reste à rédiger par l'étudiante.

## Résultat principal

Modèle sélectionné : **SARIMA(2,1,1)(0,1,1)[7]**. Sur le test externe, RMSE **82,38 GWh/jour**, contre **113,93** pour le naïf saisonnier. Couverture observée des intervalles nominaux à 95 % : **94,36 %**. Les diagnostics résiduels restent défavorables ; le rapport les expose.

Les sept prévisions concernent le **1er–7 septembre 2026**, après la dernière observation du 31 août 2026. Elles ne sont pas des prévisions pour octobre.

## Organisation

| Chemin | Rôle |
|---|---|
| `01_preparation_donnees.ipynb` à `04_visualisations.ipynb` | Travail fourni par Fayfa, conservé tel quel |
| `data/daily.csv` | 3 896 observations quotidiennes, cible `conso_gwh` |
| `arima_sarima.ipynb` | Partie prévision exécutée |
| `scripts/finalisation.py` | Complément de modèles, sélection, test et exports |
| `scripts/executer_comparaison.py` | Exécution de toutes les cellules du notebook |
| `exports/` | Tableaux, prévisions, diagnostics, paramètres et métadonnées |
| `figures/arima_sarima/` | Graphiques de cette partie |
| `rapport/` | Sections du rapport et annexe LLM |
| `tests/` | Vérifications du protocole glissant |
| `livraison_anas/` | Dossier prêt à transmettre |

## Reproduire la partie prévision

Ouvrir le dossier à sa racine. L'environnement `.venv` local est déjà installé pour les calculs de cette partie. Dans VS Code, sélectionner son interpréteur pour le notebook. Pour une nouvelle installation :

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Les versions exactes de l'environnement de calcul (Python 3.9 sur macOS) sont dans `requirements-lock.txt`. Pour cet environnement, pmdarima 2.0.4 utilise NumPy < 2 ; consulter les [notes officielles de pmdarima](https://github.com/alkaline-ml/pmdarima/releases) avant de modifier cet ensemble de versions.

```sh
.venv/bin/python scripts/executer_comparaison.py
.venv/bin/python scripts/preparer_rapport.py
.venv/bin/python scripts/preparer_livraison.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/verifier_livrables.py
```

Le script d'exécution enregistre les sorties dans le notebook : fermer/recharger l'éditeur pour éviter d'écraser ces sorties avec une ancienne version ouverte. La recherche automatique peut prendre quelques minutes et émettre des avertissements de candidats non convergés ; les modèles finalement utilisés doivent converger.

Les réponses LLM sont des archives de cette session, pas des textes régénérés automatiquement par un script. Si les données ou les paramètres changent, conserver l'ancienne annexe, puis en préparer une nouvelle et actualiser la section 5. Le vérificateur contrôle que son contexte reste cohérent avec les résultats.

## Méthode et limites

Découpage externe de Fayfa : 3 506 jours jusqu'au 6 août 2025 pour l'apprentissage ; 390 jours de test à partir du 7 août 2025. La sélection utilise huit semaines de validation interne et reste exploratoire (EDA préalable et réutilisation de la validation). Les ordres sont figés avant le test externe. Les paramètres restent fixes durant chaque évaluation glissante ; seuls les états sont actualisés.

Les sources brutes `data/raw/` ne sont pas incluses dans l'archive. La préparation de Fayfa ne peut donc pas être réexécutée entièrement en l'état ; ses autres notebooks et leurs résultats n'ont pas été recalculés ici. Les modèles de prévision utilisent directement `data/daily.csv`.

Aucun fichier n'a été envoyé à Anas et aucun dépôt GitHub n'a été publié. Le `.gitignore` exclut l'environnement et les fichiers techniques ; les résultats scientifiques restent partageables sous réserve des droits sur les données.
