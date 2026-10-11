## 4.2 Approche hybride : SARIMA + LSTM

### Principe

Le SARIMA(2,1,1)(0,1,1)[7] de la section 3.1 fournit une première prévision ; un LSTM apprend à prévoir son **erreur** eₜ = yₜ − ŷₜ(SARIMA), et la prévision hybride est ŷₜ(SARIMA) + êₜ. L'idée est de laisser l'économétrie traiter la saisonnalité hebdomadaire et le réseau capter la structure non linéaire restante. Pour que le LSTM apprenne sur des erreurs semblables à celles du test, nous générons des erreurs de prévision par blocs de 7 jours, à paramètres fixes, du 5 janvier 2017 (après un an de démarrage du filtre) à la fin de chaque période d'ajustement, soit environ 3 000 erreurs. Le SARIMA est estimé jusqu'au 11 juin 2025 pour la validation, jusqu'au 6 août 2025 pour le test et jusqu'au 31 août 2026 pour la prévision finale ; le LSTM des erreurs est chaque fois réentraîné (mêmes hyperparamètres que ceux du tableau @tab:hyperparametres).

**Nature pseudo hors échantillon de l'hybride.** Les paramètres du SARIMA sont estimés sur la même période que celle où nous générons ses erreurs d'apprentissage : les paramètres ont vu les données, seuls les états du filtre sont mis à jour hors échantillon. Ces erreurs sont donc *pseudo hors échantillon* et peuvent être un peu plus petites que celles du test, ce qui avantage légèrement l'apprentissage du LSTM. Le SARIMA recalculé dans le notebook coïncide avec celui de la section 3.1 : les écarts maximaux sont de 0,0094 GWh en validation, de 0,0192 GWh sur le test et de 0,0003 GWh pour la prévision finale.

### Validation et test

[[TAB:hybride|Hybride SARIMA + LSTM : validation et test|L'hybride améliore la RMSE de validation (36,60 contre 42,67) puis la RMSE de test de 3,0 %, mais pas la MAE ni la MAPE.]]

| Modèle | Entrées du LSTM des erreurs | RMSE de validation | RMSE de test | MAE de test | MAPE de test |
|---|---|---|---|---|---|
| SARIMA seul | — | 42,67 | 82,38 | 53,12 | 4,13 % |
| SARIMA + LSTM | consommation seule | 44,81 | — | — | — |
| SARIMA + LSTM | consommation et calendrier (retenu) | **36,60** | **79,92** | 53,84 | 4,27 % |

Toutes les erreurs sont en GWh/jour. Comme pour les réseaux directs, le calendrier est retenu sur la validation. L'hybride réduit la RMSE du SARIMA de 3,0 % sur le test, mais **pas sa MAE ni sa MAPE**, qui augmentent légèrement. La différence de RMSE n'est pas significative : p = 0,595 brute et 1,00 après correction de Holm (perte quadratique), et le test avec la perte absolue donne le même verdict (p corrigée de 1,00). L'hybride n'est pas non plus distinguable du LSTM seul (p brute de 0,23). Les modèles emboîtés (SARIMA et hybride) demandent en outre une interprétation prudente des tests.

[[FIG:hybride|../figures/lstm_gru/42_hybride_sarima_lstm.png|Prévisions de l'hybride SARIMA + LSTM|L'hybride suit de près le SARIMA ; la correction du LSTM reste modeste.]]

### Limites

Les erreurs d'apprentissage sont pseudo hors échantillon ; la validation est courte et estivale ; l'hybride ne fournit pas d'intervalle de prévision ; le gain de RMSE n'est pas établi statistiquement.
