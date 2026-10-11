# 1 — Données : source, période et transformations

## 1.1 Sources et période

La consommation provient du jeu **« Données éCO2mix nationales consolidées et définitives »** de RTE, diffusé par ODRÉ (identifiant `eco2mix-national-cons-def`) ; la température provient du jeu **« Température quotidienne régionale »** d'ODRÉ (identifiant `temperature-quotidienne-regionale`). Les deux couvrent la France métropolitaine du 1er janvier 2016 au 31 août 2026 après coupure (la température s'étend jusqu'au 30 septembre 2026 et a été tronquée pour coïncider avec la consommation).

## 1.2 Transformations appliquées par le fournisseur

- **Consommation.** RTE publie des données *définitives* (après contrôle) et des données *consolidées* (plus récentes, encore susceptibles d'être révisées). La colonne `nature` conserve cette information : 3 653 jours sont « définitifs » (du 1er janvier 2016 au 31 décembre 2025) et 243 jours « consolidés » (du 1er janvier au 31 août 2026). **Le test externe contient donc des valeurs consolidées**, éventuellement révisées plus tard par RTE. Le fichier source compte 374 016 lignes au pas de 15 minutes, dont 187 009 sont vides : la consommation est mesurée toutes les 30 minutes (48 valeurs par jour).
- **Température.** ODRÉ fournit, pour chacune des 13 régions métropolitaines, une température minimale, maximale et moyenne quotidienne. Nous ne disposons d'aucune documentation du fournisseur sur d'éventuelles corrections d'homogénéisation et n'en appliquons aucune.

## 1.3 Transformations appliquées par le groupe

1. **Agrégation journalière.** Nous calculons la moyenne des puissances (MW) sur la journée, multipliée par 24 h et divisée par 1 000, pour obtenir des GWh/jour. La moyenne est indépendante du pas de mesure, contrairement à une somme. Chaque jour compte 48 mesures non vides, sauf le 1er janvier 2026 (47 mesures).
2. **Température nationale.** Moyenne simple des 13 régions, non pondérée par la population (limite : la Corse pèse autant que l'Île-de-France). 37 jours absents du fichier ODRÉ, en trous isolés de un ou deux jours, sont comblés par interpolation linéaire dans le temps et signalés par `temp_interpolee = 1`.
3. **Variables dérivées.** `hdd` = max(0, 18 − T) et `cdd` = max(0, T − 21), où T est la température moyenne en °C ; `ferie` (118 jours fériés français) ; `jour_semaine` (0 = lundi, …, 6 = dimanche).
4. **Série temporelle native.** Le fichier `data/daily.csv` est lu avec un `DatetimeIndex` journalier de fréquence déclarée (`asfreq('D')`) : 3 896 dates consécutives, sans doublon ni trou. Les jeux de données source et préparé sont décrits ci-dessous.

[[TAB:variables|Variables du jeu de données préparé|Seules la consommation, la température et le calendrier sont utilisés par les modèles ; les autres colonnes servent à l'analyse exploratoire.]]

| Variable | Contenu | Unité |
|---|---|---|
| `conso_gwh` | consommation électrique (cible) | GWh/jour |
| `temp_moy`, `temp_min`, `temp_max` | température nationale moyenne, minimale, maximale | °C |
| `hdd`, `cdd` | degrés-jours de chauffage et de climatisation | °C |
| `ferie`, `jour_semaine` | jour férié, jour de la semaine | indicatrice, 0 à 6 |
| `nucleaire_gwh`, `gaz_gwh`, `eolien_gwh`, `solaire_gwh`, `taux_co2` | production par filière, intensité carbone | GWh/jour, g/kWh |
| `temp_interpolee`, `nature` | jour interpolé, statut RTE (définitif ou consolidé) | indicatrice, texte |

## 1.4 Découpage chronologique 90 % / 10 %

Le découpage décrit en introduction (tableau @tab:decoupage) donne **3 506 jours d'apprentissage et 390 jours de test**. Toutes les analyses exploratoires et tous les choix de modèles sont faits sur l'apprentissage ; le test n'est utilisé que pour mesurer les performances.

## 1.5 Reproductibilité de la préparation

Les fichiers bruts (`data/raw/`) ne sont pas fournis, en raison de leur taille. Si `data/raw/` est absent, le notebook `01_preparation_donnees.ipynb` affiche les adresses de téléchargement des deux fichiers et utilise `data/daily.csv`, qui est fourni. Les autres notebooks partent de `data/daily.csv`.
