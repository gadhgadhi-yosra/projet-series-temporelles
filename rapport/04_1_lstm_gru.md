# 4 — Modélisation avancée

Cette section traite des réseaux de neurones récurrents (4.1), d'une approche hybride économétrique et neuronale (4.2) et de Prophet (4.3). Les réseaux et l'hybride sont implémentés en Python (PyTorch, notebook `07_lstm_gru.ipynb`).

## 4.1 Réseaux de neurones récurrents : LSTM et GRU

### Mise en forme des données et architecture

Un **LSTM** (*Long Short-Term Memory*) garde une mémoire interne contrôlée par trois portes (oubli, entrée, sortie). Un **GRU** (*Gated Recurrent Unit*) la simplifie avec deux portes et compte donc moins de paramètres. Les deux réseaux ont la même taille et le même protocole ; seule la cellule récurrente diffère. Chaque exemple est une **fenêtre glissante** de 28 jours (consommation passée et calendrier) ; la cible est la consommation du jour suivant. Le calendrier (sinus et cosinus du jour de la semaine, indicatrice de jour férié) est connu à l'avance ; **aucune donnée météo ni valeur future n'est utilisée**. La consommation est **centrée-réduite** avec la moyenne et l'écart-type de la seule période d'apprentissage de chaque ajustement. La prévision est **récursive par blocs de 7 jours** : dans un bloc, chaque prévision sert d'entrée pour le jour suivant, et les vraies valeurs ne sont ajoutées qu'au bloc suivant. Les paramètres du réseau restent fixes pendant tout le test.

[[TAB:hyperparametres|Hyperparamètres des réseaux récurrents et justification|Une seule architecture a été essayée : seuls les entrées et le nombre d'époques ont été choisis sur la validation.]]

| Hyperparamètre | Valeur | Justification |
|---|---|---|
| Taille de fenêtre | 28 jours | quatre cycles hebdomadaires complets ; valeur fixée a priori, non optimisée |
| Nombre de couches récurrentes | 1 | peu d'exemples (environ 3 400 fenêtres) : un réseau plus profond surajusterait ; non comparé à une architecture plus profonde |
| Unités cachées | 32 | 4 900 paramètres pour le LSTM et 3 684 pour le GRU, de l'ordre du nombre d'exemples ; non optimisé |
| Dropout | aucun | non testé ; l'arrêt anticipé joue le rôle de régularisation |
| Optimiseur, taux d'apprentissage, lot | Adam, 0,001, 64 | valeurs standard |
| Époques | 40 au plus, arrêt anticipé (patience 7) | meilleure époque retenue sur la validation uniquement |
| Graines | 5 (42 à 46) | la prévision est la moyenne de 5 réseaux, ce qui réduit la dépendance à l'initialisation |

### Procédure d'entraînement et courbes de perte

[[FIG:courbes_perte|../figures/lstm_gru/courbes_perte_train_validation.png|Perte d'apprentissage et de validation du LSTM et du GRU|La perte d'apprentissage décroît régulièrement ; la validation se stabilise vers l'époque 33 (LSTM) et 35 (GRU), puis oscille sans progresser.]]

La perte d'apprentissage (erreur quadratique moyenne des mini-lots, exprimée en RMSE) passe d'environ 170–200 GWh/jour à 35 GWh/jour, tandis que la RMSE de validation passe d'environ 68 à 38–39 GWh/jour ; le premier point de la courbe d'apprentissage est élevé car il moyenne la perte pendant la première époque, réseau non entraîné compris. Au-delà de l'époque retenue (33 pour le LSTM et 35 pour le GRU avec la graine 42, ce qui reproduit les valeurs du notebook), la validation oscille entre 38 et 52 GWh/jour (LSTM) et entre 39 et 49 GWh/jour (GRU) sans progresser, alors que l'apprentissage reste plat : l'arrêt anticipé limite ce début de surapprentissage.

### Choix des entrées sur la validation

[[TAB:entrees|Choix des entrées sur la validation interne|Le calendrier améliore nettement les deux réseaux : il est retenu.]]

| Modèle | Entrées | RMSE de validation (GWh/jour) |
|---|---|---|
| LSTM | consommation seule | 46,55 |
| LSTM | consommation et calendrier | **39,37** |
| GRU | consommation seule | 50,06 |
| GRU | consommation et calendrier | **38,88** |

### Validation croisée temporelle (walk-forward)

Nous évaluons la robustesse par une validation croisée **à fenêtre croissante** (walk-forward), jamais par un k-fold aléatoire. Chaque pli apprend sur toute la série disponible jusqu'à sa date d'origine, puis prévoit les **56 jours suivants** par blocs de 7 jours. Les cinq plis sont **entièrement situés dans l'apprentissage** (le test externe n'est jamais utilisé) et comprennent **trois plis d'hiver et deux plis d'été**. Les hyperparamètres, les entrées, la normalisation par pli, les cinq graines et le nombre d'époques (celui retenu par arrêt anticipé au notebook 07, appliqué sans nouvel arrêt) sont identiques pour tous les plis. Le SARIMA est réestimé sur chaque pli ; le naïf saisonnier n'a aucun paramètre.

[[TAB:cv|Validation croisée temporelle : RMSE par pli (GWh/jour)|Le GRU bat le SARIMA dans les cinq plis et le LSTM dans quatre ; tous les modèles se dégradent fortement en hiver.]]

| Pli | Période de test | Saison | Jours d'apprentissage | LSTM | GRU | SARIMA | Naïf saisonnier |
|---|---|---|---|---|---|---|---|
| 1 | 20/12/2021 – 13/02/2022 | hiver | 2 180 | 130,09 | **124,44** | 145,91 | 204,24 |
| 2 | 19/12/2022 – 12/02/2023 | hiver | 2 544 | 190,43 | **183,12** | 203,72 | 221,90 |
| 3 | 12/06/2023 – 06/08/2023 | été | 2 719 | 34,33 | **27,42** | 31,89 | 40,02 |
| 4 | 16/12/2024 – 09/02/2025 | hiver | 3 272 | **103,87** | 108,83 | 115,27 | 164,84 |
| 5 | 12/06/2025 – 06/08/2025 | été | 3 450 | 39,37 | **38,87** | 42,67 | 55,22 |
| | **Moyenne des cinq plis** | | | 99,62 | **96,54** | 107,89 | 137,24 |
| | Moyenne des plis d'hiver | | | 141,46 | **138,80** | 154,97 | 196,99 |
| | Moyenne des plis d'été | | | 36,85 | **33,14** | 37,28 | 47,62 |
| | Rang moyen (1 = meilleur) | | | 2,0 | **1,2** | 2,8 | 4,0 |

Les deux réseaux font mieux que le SARIMA en moyenne (96,54 pour le GRU et 99,62 pour le LSTM contre 107,89 GWh/jour) et que le naïf saisonnier (137,24). Le GRU est le meilleur modèle dans quatre plis sur cinq (le LSTM dans le quatrième) ; le LSTM est battu par le SARIMA dans le pli d'été 3. Ces classements sont stables d'un pli à l'autre, ce qui renforce la conclusion du test externe, mais plusieurs réserves s'imposent. Les erreurs d'hiver (de 104 à 222 GWh/jour selon le pli et le modèle) sont environ quatre fois plus grandes que celles d'été (de 27 à 55 GWh/jour) : ce sont les fenêtres de 56 jours les plus difficiles, et leurs RMSE ne sont pas comparables à la RMSE du test (390 jours, toutes saisons). L'écart-type entre plis (64 GWh/jour pour le GRU) est dominé par la saison. Cinq plis ne permettent pas de test de significativité fiable : ces différences restent **descriptives**. Enfin, le pli 5 coïncide avec la validation interne qui a servi à choisir les entrées et les époques : il reproduit exactement les valeurs de validation du notebook (39,37, 38,87 et 42,67) et est donc légèrement optimiste pour les réseaux.

[[FIG:cv|../figures/lstm_gru/cv_temporelle.png|RMSE par pli de la validation croisée temporelle|Dans chaque pli, le naïf saisonnier est le moins précis ; l'écart entre réseaux et SARIMA est plus marqué en hiver.]]

### Résultats sur le test externe

Les réseaux sont réentraînés jusqu'au 6 août 2025 avec le nombre d'époques retenu, puis prévoient les 390 jours de test (section 6, tableau @tab:scores). Le **LSTM obtient une RMSE de 75,07 GWh/jour** (MAE 50,26 GWh/jour, MAPE 3,96 %) et le **GRU de 76,40 GWh/jour** (MAE 52,40 GWh/jour, MAPE 4,16 %), contre 82,38 GWh/jour pour le SARIMA ; le gain de RMSE du LSTM sur le naïf saisonnier est de 34,1 %. Sur le test, le LSTM devance donc le GRU, alors que c'est l'inverse dans quatre plis de la validation croisée : l'écart entre les deux réseaux est trop faible pour les départager (test de Diebold–Mariano, section 6, p corrigée de 1,00). Les réseaux fournissent des prévisions ponctuelles, sans intervalle.

### Limites

Une seule architecture a été essayée (une couche, 32 unités, fenêtre de 28 jours, sans dropout) ; un réglage plus large demanderait une validation plus longue pour ne pas surajuster. La validation interne est courte et estivale (56 jours) : elle ne contient pas de vague de froid, alors que les plus grosses erreurs surviennent en hiver. Aucune météo n'est utilisée.
