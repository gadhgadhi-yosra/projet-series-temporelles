## 4.3 Modèle additionnel : Prophet

Prophet décompose la série en une tendance linéaire par morceaux, des saisonnalités (annuelle, hebdomadaire) et des effets de jours fériés (colonne `ferie`). Il n'a pas de terme autorégressif. Nous comparons en validation interne deux niveaux de flexibilité de la tendance (`changepoint_prior_scale` de 0,05 et de 0,5) et deux modes de saisonnalité (additif et multiplicatif).

[[TAB:prophet_validation|Choix des hyperparamètres de Prophet sur la validation interne|La tendance flexible additive est la meilleure ; la série contient des ruptures (2020, 2022-23) que la tendance rigide suit mal.]]

| Flexibilité de la tendance | Mode | RMSE de validation (GWh/jour) | MAE de validation (GWh/jour) |
|---|---|---|---|
| 0,05 | additif | 60,28 | 45,07 |
| 0,05 | multiplicatif | 57,13 | 41,94 |
| **0,5** | **additif** | **51,90** | 38,83 |
| 0,5 | multiplicatif | 52,48 | 38,34 |

Prophet n'ayant pas d'état à actualiser, il est **réajusté tous les 7 jours** sur l'historique disponible (56 ajustements pour le test), alors que les autres modèles gardent des paramètres fixes ; cet avantage de protocole doit être gardé en tête dans la comparaison. Les résidus d'apprentissage sont très autocorrélés et hétéroscédastiques (Ljung-Box et ARCH-LM : p ≈ 0 ; kurtosis 4,94), ce qui est attendu sans terme autorégressif.

[[FIG:prophet|../figures/ghada/prophet_composantes.png|Composantes de Prophet|Prophet capte la tendance (baisse en 2020 et 2022-23), la saisonnalité annuelle et le creux du week-end, mais ces composantes ne remplacent pas une mémoire à court terme.]]

Sur le test, **Prophet obtient une RMSE de 101,79 GWh/jour** (MAE 75,06 GWh/jour, MAPE 5,91 %) et une couverture de 88,5 % (intervalles trop étroits : seule l'incertitude de la tendance et du bruit est prise en compte). Une variante à ajustement unique, qui prévoit directement jusqu'à 390 jours, obtient une RMSE de 97,57 GWh/jour avec une couverture de 97,4 % mais des intervalles de 890,7 GWh/jour de large : elle n'est pas comparable au protocole à sept jours. Prophet fait mieux que les références naïves (109,13 et 113,93 GWh/jour) mais moins bien que le SARIMA (82,38) ; il est utile pour lire la tendance et les saisonnalités, pas pour la prévision à sept jours, faute de mémoire à court terme (RMSE de 99,63 GWh/jour dès l'horizon 1). Prophet n'a pas été répliqué en R.
