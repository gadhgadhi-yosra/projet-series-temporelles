## Conclusion

**Meilleur modèle observé selon la RMSE : AR-GARCH(1,2)-t.** Sur les 390 jours du test externe, il obtient MSE = 5543.30 (GWh/jour)², RMSE = 74.45 GWh/jour, MAE = 48.61 GWh/jour et MAPE = 3.78 %.

Le meilleur réseau récurrent est **LSTM** (RMSE 75.07), contre 76.40 pour l’autre réseau. Son gain de RMSE par rapport au naïf saisonnier est de 34.1 % (un gain négatif indique une dégradation).

L’hybride **SARIMA + LSTM** obtient RMSE 79.92, contre 82.38 pour SARIMA : il réduit la RMSE de 3.0 %. La différence est non significative à 5 % après Holm (p ajustée = 1.0000).

Les tests de Diebold–Mariano par blocs **ne distinguent pas significativement AR-GARCH(1,2)-t** des modèles suivants à 5 % après correction de Holm : LSTM, GRU, VAR(3), SARIMA + LSTM, SARIMA, VECM(12, r=1), Naïf saisonnier. Une différence non significative ne démontre pas leur équivalence.

Gagnants par critère : MSE : AR-GARCH(1,2)-t; RMSE : AR-GARCH(1,2)-t; MAE : AR-GARCH(1,2)-t; MAPE (%) : AR-GARCH(1,2)-t.

Pour une prévision ponctuelle dans ce cadre, **AR-GARCH(1,2)-t est le candidat principal selon la RMSE observée**. Ce choix reste descriptif : les architectures ont été choisies sur la validation, et le classement final sur le test demande une nouvelle période indépendante avant de conclure à une supériorité durable. La validation est courte et estivale, le test couvre un seul hiver, aucune météo future n’est utilisée et les erreurs d’apprentissage de l’hybride sont pseudo hors échantillon. Prophet est réajusté chaque semaine ; cette différence de protocole et les limites des tests doivent être conservées.
