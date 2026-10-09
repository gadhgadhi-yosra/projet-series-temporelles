## Résultats de la première comparaison — aide IA à discuter

Calculs exécutés sur les données réelles. Estimation : 3 450 jours jusqu'au 11 juin 2025 ; validation : huit semaines du 12 juin au 6 août 2025. Les 390 jours de test externe restent réservés.

| Modèle | MAE (GWh/jour) | RMSE (GWh/jour) |
|---|---:|---:|
| SARIMA(1,1,0)(0,1,1)[7] | 31,11 | 42,97 |
| SARIMA(1,1,0)(1,0,1)[7] | 31,14 | 43,01 |
| SARIMA(0,1,1)(0,1,1)[7] | 30,99 | 43,05 |
| auto_SARIMA : (2,1,1)(1,0,0)[7] | 36,83 | 48,10 |
| Naïf saisonnier | 44,04 | 55,22 |
| auto_ARIMA : (2,1,2) | 59,01 | 74,23 |
| Dernière valeur | 67,73 | 88,59 |

**Interprétation provisoire.** La plus petite RMSE revient à SARIMA(1,1,0)(0,1,1)[7], mais les trois premiers modèles sont presque à égalité. La plus petite MAE revient à SARIMA(0,1,1)(0,1,1)[7]. La variante D=0 est compétitive : D=1 n'est donc pas un choix acquis. La recherche automatique minimise un critère d'information sur l'estimation, pas l'erreur de validation ; elle ne gagne pas nécessairement sur les prévisions.

**Diagnostics.** Pour tous les modèles estimés, les p-values Ljung–Box aux retards 7 et 14 sont inférieures à 0,05. Jarque–Bera et ARCH-LM rejettent aussi leurs hypothèses nulles. Les résidus gardent une structure temporelle, ne sont pas compatibles avec la normalité selon ce test et montrent des effets ARCH. Les p-values affichées à 0 sont des limites numériques d'affichage/calcul, pas des probabilités exactement nulles démontrées.

**Conséquence.** Aucun modèle n'est encore déclaré validé. Examiner les résidus et les effets hebdomadaires/annuels non représentés avant de figer le choix. La validation ne couvre que huit semaines d'été et l'EDA initiale de Fayfa l'avait déjà consultée : ces résultats restent exploratoires. Une amélioration de RMSE sur cette période ne garantit pas un gain sur toute l'année. Ne pas utiliser le test externe pour ajuster les ordres.

Les tableaux complets sont dans `exports/comparaison_validation_interne.csv`, `exports/predictions_validation_interne.csv` et `exports/diagnostics_estimation.csv`. L'analyse personnelle de la section 5 reste à rédiger par l'étudiante ; ce résumé est une assistance IA.
