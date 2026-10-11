# 6 — Prévision et évaluation comparative

Cette section compare les dix modèles sur le test externe (notebook `07_lstm_gru.ipynb`, dossier `exports/lstm_gru/`). Les temps et les nombres de paramètres proviennent de `scripts/mesures_complexite.py` (`exports/complexite_modeles.csv`).

## 6.1 Conclusion sur le modèle final

Sur le test (390 jours), AR-GARCH(1,2)-t a la plus petite erreur (RMSE 74,45 GWh/jour), mais aucun test de Diebold–Mariano corrigé (Holm) ne le distingue de SARIMA, LSTM, GRU, VAR(3) ni de l'hybride. SARIMA(2,1,1)(0,1,1)[7] est le modèle retenu par la règle de validation interne ; AR-GARCH est le meilleur observé sur le test, à égalité avec le GRU en validation croisée ; nous ne concluons pas à une supériorité durable. Le témoin « AR à variance constante » (AR sur les retards 1, 2, 7, 8 et 14, même calendrier, sans GARCH) obtient une RMSE de **74,06 GWh/jour**, légèrement meilleure : le gain vient de la moyenne autorégressive avec calendrier, non de la modélisation de la variance, qui améliore en revanche la couverture des intervalles (95,9 % contre 93,3 %), sans les rendre assez larges en hiver (section 6.6).

## 6.2 Protocole de comparaison

Tous les modèles prévoient **les mêmes 390 jours** (du 7 août 2025 au 31 août 2026), avec les mêmes 55 blocs complets de 7 jours, un dernier bloc de 5 jours et les mêmes horizons de 1 à 7 jours ; le code vérifie dates, observations et horizons. Les différences de protocole à garder en tête sont les suivantes.

- **Prophet est réajusté chaque semaine**, alors que SARIMA, VAR, VECM, AR-GARCH et les réseaux gardent des **paramètres fixes** pendant tout le test (seuls leurs états ou leurs entrées sont actualisés) : Prophet bénéficie de réestimations que les autres n'ont pas.
- **L'hybride SARIMA + LSTM est pseudo hors échantillon** (section 4.2).
- **Les tests de Diebold–Mariano utilisent 385 jours** (55 blocs complets de 7 jours), contre **390 jours pour les métriques** : les cinq derniers jours (bloc incomplet) sont exclus des tests pour garder sept horizons à chaque origine.
- **Calendrier** : VAR, VECM, AR-GARCH, Prophet et les réseaux utilisent des régresseurs de calendrier que le SARIMA de la section 3.1 n'a pas ; la comparaison les avantage et ne prouve pas qu'ils soient intrinsèquement meilleurs.
- Aucun modèle n'utilise de prévision météo.

## 6.3 Tableau récapitulatif des modèles

[[TAB:scores|Comparaison des modèles sur le test externe (390 jours)|AR-GARCH a la plus petite erreur et la seule couverture qui atteint 95 % sur ce test ; les réseaux sont juste derrière mais plus coûteux et opaques ; Prophet et les naïfs sont nettement en retrait.]]

| Modèle | MSE | RMSE | MAE | MAPE (%) | Couverture à 95 % | Paramètres | Temps d'un ajustement (s) | Interprétabilité |
|---|---|---|---|---|---|---|---|---|
| AR-GARCH(1,2)-t | 5 543,30 | **74,45** | 48,61 | 3,78 | 95,9 % | 25 | 0,10 | élevée |
| LSTM | 5 634,84 | 75,07 | 50,26 | 3,96 | — | 4 900 | 7,73 (× 5) | faible |
| GRU | 5 836,62 | 76,40 | 52,40 | 4,16 | — | 3 684 | 15,18 (× 5) | faible |
| VAR(3) | 6 234,26 | 78,96 | 54,67 | 4,31 | 93,1 % | 40 | 0,02 | élevée |
| SARIMA + LSTM | 6 387,63 | 79,92 | 53,84 | 4,27 | — | 4 905 | 10,60 (× 6) | moyenne |
| SARIMA(2,1,1)(0,1,1)[7] | 6 786,82 | 82,38 | 53,12 | 4,13 | 94,4 % | 5 | 2,08 | élevée |
| VECM(12, r = 1) | 7 667,09 | 87,56 | 58,71 | 4,61 | 91,3 % | 79 | 0,02 | moyenne |
| Prophet (réajusté chaque semaine) | 10 361,04 | 101,79 | 75,06 | 5,91 | 88,5 % | 55 | 1,78 (× 56) | élevée |
| Persistance (dernière valeur) | 11 909,59 | 109,13 | 76,63 | 6,46 | — | 0 | 0 | totale |
| Naïf saisonnier (semaine précédente) | 12 979,43 | 113,93 | 76,66 | 5,97 | — | 0 | 0 | totale |
| *Témoin : AR creux, variance constante* | 5 485,24 | 74,06 | 49,16 | 3,84 | 93,3 % | 21 | 0,01 | élevée |

Les erreurs (MSE en (GWh/jour)², autres en GWh/jour) sont calculées sur les 390 jours. Le temps est celui d'un ajustement sur les 3 506 jours d'apprentissage, sur un seul fil de calcul ; le facteur entre parenthèses est le nombre d'ajustements du protocole (5 graines pour les réseaux, 56 réajustements hebdomadaires pour Prophet, SARIMA et 5 réseaux pour l'hybride). Le témoin n'est pas dans le classement à dix modèles ; il est donné pour mémoire (21 paramètres : régression de calendrier, AR creux et variance constante). Les temps varient d'environ 15 % d'une exécution à l'autre. L'hybride a une RMSE inférieure à celle du SARIMA mais une MAE et une MAPE supérieures ; l'ordre des modèles voisins change donc selon la métrique.

**Interprétabilité.** Nous la jugeons élevée quand les paramètres ont une lecture directe : coefficients autorégressifs du SARIMA, du VAR et de l'AR-GARCH (avec réponse impulsionnelle et variance conditionnelle), composantes visualisables de Prophet. Elle est moyenne pour le VECM, dont l'équilibre et la vitesse de correction ne sont pas robustes, et pour l'hybride, qui mêle un SARIMA lisible à un réseau opaque. Elle est faible pour le LSTM et le GRU, dont les milliers de poids n'ont pas de lecture individuelle.

### Erreur selon l'horizon

[[FIG:horizon|../figures/lstm_gru/6_rmse_par_horizon.png|RMSE selon l'horizon de prévision|À l'horizon 1, les modèles dynamiques sont à égalité ; l'erreur croît ensuite, et l'avantage d'AR-GARCH apparaît aux horizons les plus longs.]]

À l'horizon 1, les modèles dynamiques (réseaux, VAR, SARIMA, VECM, persistance) sont à égalité, avec une RMSE de 32 à 38 GWh/jour : la persistance de la consommation suffit. L'erreur croît ensuite jusqu'à 96–111 GWh/jour à l'horizon 7 ; Prophet, sans mémoire à court terme, est mauvais dès l'horizon 1 (99,63 GWh/jour). Le détail est en annexe A (tableau @tab:annexe_horizon).

## 6.4 Prévisions du 1er au 7 septembre 2026

Chaque modèle est réestimé sur toutes les observations jusqu'au 31 août 2026 et prévoit les sept jours suivants (horizon h = 7) ; ces prévisions ne concernent pas octobre. Les valeurs réelles de septembre ne figurent pas dans `data/daily.csv` : aucune erreur ne peut donc être calculée.

[[TAB:previsions|Prévisions de consommation du 1er au 7 septembre 2026 (GWh/jour)|Les huit modèles s'accordent à moins de 35 GWh/jour près chaque jour ; tous reproduisent le creux du week-end (5 et 6 septembre).]]

| Date | SARIMA | SARIMA + LSTM | LSTM | GRU | AR-GARCH | VAR(3) | VECM | Prophet |
|---|---|---|---|---|---|---|---|---|
| 1er septembre (mardi) | 1 086,54 | 1 093,08 | 1 095,60 | 1 087,80 | 1 079,10 | 1 097,54 | 1 100,64 | 1 090,11 |
| 2 septembre (mercredi) | 1 090,60 | 1 096,77 | 1 096,01 | 1 090,15 | 1 082,29 | 1 102,98 | 1 110,17 | 1 094,77 |
| 3 septembre (jeudi) | 1 085,84 | 1 083,02 | 1 100,61 | 1 087,40 | 1 082,22 | 1 099,00 | 1 108,48 | 1 094,20 |
| 4 septembre (vendredi) | 1 074,40 | 1 069,49 | 1 086,72 | 1 070,77 | 1 064,36 | 1 083,43 | 1 086,69 | 1 080,21 |
| 5 septembre (samedi) | 977,91 | 969,79 | 980,75 | 962,05 | 954,01 | 973,08 | 977,74 | 972,48 |
| 6 septembre (dimanche) | 938,23 | 930,29 | 936,71 | 910,15 | 906,98 | 923,66 | 933,00 | 925,55 |
| 7 septembre (lundi) | 1 056,45 | 1 044,81 | 1 078,25 | 1 046,23 | 1 049,73 | 1 067,23 | 1 071,65 | 1 071,15 |

[[FIG:previsions|../figures/lstm_gru/6_previsions_septembre_2026.png|Prévisions du 1er au 7 septembre 2026|Les prévisions des huit modèles forment un faisceau étroit autour du profil hebdomadaire attendu.]]

Les **intervalles de prévision à 95 %** des modèles qui en fournissent (SARIMA, VAR, VECM, AR-GARCH, Prophet) figurent en annexe A (tableau @tab:annexe_intervalles) ; les réseaux et l'hybride ne donnent que des prévisions ponctuelles. Les intervalles sont nominaux : ils sont gaussiens (sauf AR-GARCH, de loi de Student) et ignorent l'incertitude sur les paramètres.

## 6.5 Significativité des écarts : test de Diebold–Mariano

Une RMSE plus faible sur la période observée ne démontre pas une meilleure précision attendue. Le test de **Diebold–Mariano** compare deux modèles sur la perte moyenne de chaque bloc complet de 7 jours (horizons 1 à 7 mélangés), avec une variance HAC de Newey–West à poids de Bartlett (3 retards hebdomadaires) et l'approximation normale. Nous testons **les 45 paires** de modèles, avec la correction de Holm sur toute la famille, séparément pour chaque perte ; une analyse de sensibilité à 1, 2 et 4 retards est exportée.

**L'étiquette « non significatif » porte sur la perte quadratique** : les conclusions formelles du notebook utilisent cette perte et les p-values corrigées ; la perte absolue est un complément exploratoire. Le nombre de rejets à 5 % sur les 45 paires dépend de la perte (p corrigées : 7 en perte quadratique, 17 en perte absolue ; p brutes : 23 et 24).

[[TAB:dm_meilleur|AR-GARCH contre chacun des autres modèles (Diebold–Mariano)|Après correction de Holm, AR-GARCH n'est distingué ni de SARIMA, ni de LSTM, GRU, VAR(3) ou de l'hybride ; il l'est de Prophet et de la persistance, et du naïf saisonnier en perte absolue seulement.]]

| Modèle comparé | p brute, perte quadratique | p corrigée, perte quadratique | p corrigée, perte absolue |
|---|---|---|---|
| LSTM | 0,913 | 1,000 | 1,000 |
| GRU | 0,712 | 1,000 | 1,000 |
| VAR(3) | 0,054 | 1,000 | 0,097 |
| SARIMA + LSTM | 0,265 | 1,000 | 1,000 |
| SARIMA | 0,037 | 0,890 | 1,000 |
| VECM(12, r = 1) | 0,036 | 0,890 | 0,053 |
| Prophet | 0,001 | 0,029 | 0,0005 |
| Persistance | < 0,001 | < 0,001 | < 0,001 |
| Naïf saisonnier | 0,004 | 0,157 | 0,0005 |

**Cas où la perte absolue donne une conclusion différente.** Dix paires sont significatives après Holm en perte absolue seulement (annexe A, tableau @tab:annexe_dm_abs) : toutes opposent un modèle dynamique au naïf saisonnier (AR-GARCH, SARIMA, LSTM, GRU, hybride, VAR(3) : p corrigées de 0,0005 à 0,040 en perte absolue contre 0,157 à 0,391 en perte quadratique), à Prophet (LSTM, SARIMA, VAR(3)) ou, pour le VECM, à la persistance. Les différences entre modèles dynamiques ne ressortent dans aucun cas. Les 45 paires figurent en annexe A (tableau @tab:annexe_dm). La correction de Holm sur 45 paires est très prudente : elle réduit fortement la puissance, et une différence non significative ne démontre pas l'équivalence des modèles.

Les comparaisons demandées par le sujet (LSTM contre GRU, meilleur réseau contre SARIMA et contre le naïf saisonnier, hybride contre SARIMA, VAR(3) contre SARIMA) ne sont pas significatives en perte quadratique après correction ; en perte absolue, seule la comparaison du meilleur réseau au naïf saisonnier l'est (p corrigée de 0,008 ; annexe A, tableau @tab:annexe_dm_questions).

## 6.6 Quel modèle pour quel usage ?

Pour un **gestionnaire de réseau** qui doit anticiper la consommation à sept jours, la performance brute ne départage pas les cinq meilleurs modèles (écarts de RMSE de 74,45 à 82,38 GWh/jour, non significatifs après correction). Le choix repose donc sur les autres critères.

[[TAB:usage|Choix du modèle selon le cas d'usage|AR-GARCH reste recommandé, malgré des intervalles trop étroits en hiver ; le GRU et le LSTM sont les meilleurs challengers, au prix de l'interprétabilité et sans intervalles.]]

| Critère | AR-GARCH(1,2)-t | SARIMA | VAR(3) | LSTM / GRU | Prophet |
|---|---|---|---|---|---|
| Précision (RMSE de test) | meilleure (74,45) | 82,38 | 78,96 | 75,07 / 76,40 | 101,79 |
| Couverture des intervalles à 95 % sur le test | 95,9 % (86,9 % sur les plis d'hiver de la validation croisée) | 94,4 % | 93,1 % | aucun | 88,5 % (trop étroits) |
| Interprétabilité | élevée | élevée | élevée | faible | élevée |
| Coût d'un ajustement | 0,10 s | 2,08 s | 0,02 s | 7,73 s / 15,18 s, × 5 graines | 1,78 s × 56 |
| RMSE moyenne de la validation croisée : cinq plis (plis d'hiver) | 96,74 (136,65) | 107,89 (154,97) | non mesurée | 99,62 / 96,54 (141,46 / 138,80) | non mesurée |

**Notre recommandation** est de retenir un modèle de type **AR-GARCH(1,2)-t** comme modèle opérationnel : il est le meilleur observé sur le test, à égalité avec le GRU en validation croisée (RMSE moyenne de 96,74 contre 96,54 GWh/jour ; annexe A, tableau @tab:annexe_cv_garch), interprétable, quasi instantané, et le seul de ces deux modèles à fournir des intervalles. **Ces intervalles sont toutefois trop étroits en hiver** : leur couverture, de 95,9 % sur le test, n'est que de 86,9 % sur les plis d'hiver de la validation croisée et de 67,9 % pendant l'hiver 2022-23. En exploitation, il faudrait les élargir en hiver ou modéliser une variance saisonnière. Le **SARIMA** reste la référence statistique justifiée par la règle de validation, et le **GRU ou le LSTM** le meilleur challenger : ils battent le SARIMA dans la quasi-totalité des plis de la validation croisée, surtout en hiver, mais sans intervalles, sans interprétation et pour un coût plus élevé. Combiner les prévisions (par exemple moyenne d'AR-GARCH et d'un réseau) est une piste naturelle, non évaluée ici. **Prophet n'est pas adapté** à la prévision à sept jours. Cette recommandation reste conditionnelle : un seul hiver de test, des écarts non significatifs, et une validation croisée où AR-GARCH n'est le meilleur dans aucun pli.
