# 3 — Modélisation classique

Cette section est le socle économétrique du projet : SARIMA (3.1), modèles multivariés VAR et VECM (3.2), volatilité conditionnelle GARCH (3.3) et réplication en R (3.4). Chaque modèle est accompagné de son diagnostic de résidus complet : test de Ljung-Box (indépendance), test de Jarque-Bera (normalité) et test ARCH-LM (homoscédasticité conditionnelle).

## 3.1 ARIMA et SARIMA

### Identification et sélection

Les graphiques ACF/PACF de la section 2.3 suggèrent d = 1, D = 1, s = 7, un terme non saisonnier d'ordre faible et un MA saisonnier d'ordre 1. Nous comparons **onze candidats manuels** (dont quatre ajoutés après l'examen des premiers diagnostics), les variantes sans différenciation saisonnière ou sans différenciation, ainsi que les recherches automatiques `auto_arima` (`pmdarima`, Python) et `auto.arima` (`forecast`, R, section 3.4). Les candidats sont estimés sur 3 450 jours et classés par RMSE sur la validation interne (huit blocs de sept jours du 12 juin au 6 août 2025, paramètres fixes). Cette validation est exploratoire : elle chevauche la période déjà vue dans l'analyse exploratoire et a servi à ajouter quatre candidats ; elle ne mesure donc pas la généralisation. L'ordre est figé **avant** le test externe.

[[TAB:sarima_selection|Sélection du modèle SARIMA sur la validation interne|Le SARIMA(2,1,1)(0,1,1)[7] a la plus petite RMSE de validation ; la différence avec les candidats voisins (42,68 à 43,05 GWh/jour) est minime, et les recherches automatiques sont nettement moins bonnes.]]

| Modèle | RMSE (GWh/jour) | MAE (GWh/jour) |
|---|---|---|
| SARIMA(2,1,1)(0,1,1)[7] (retenu) | 42,68 | 32,60 |
| SARIMA(2,1,2)(0,1,1)[7] | 42,81 | 32,74 |
| SARIMA(1,1,0)(0,1,1)[7] | 42,97 | 31,11 |
| SARIMA(0,1,1)(0,1,1)[7] (modèle « airline ») | 43,05 | 30,99 |
| `auto_arima`, Python : SARIMA(2,1,1)(1,0,0)[7] | 48,11 | 36,83 |
| `auto.arima`, R : SARIMA(1,0,1)(1,1,0)[7] | 49,77 | 38,83 |
| Naïf saisonnier (semaine précédente) | 55,22 | 44,04 |
| `auto_arima` sans saisonnalité : ARIMA(2,1,2) | 74,23 | 59,01 |
| Naïf « dernière valeur » | 88,59 | 67,73 |

La comparaison des deux approches automatiques montre que `pmdarima` et `auto.arima` ne retrouvent pas le modèle identifié par l'ACF/PACF : leurs recherches pas à pas explorent l'espace dans un ordre différent, et aucune ne bat le SARIMA(2,1,1)(0,1,1)[7]. Le tableau complet des 15 modèles (avec AIC et BIC, à interpréter avec prudence entre différenciations différentes) figure en annexe A (tableau @tab:annexe_sarima). Une faible différence de RMSE entre candidats ne démontre pas une supériorité statistique.

### Diagnostic des résidus

Les résidus du modèle retenu, estimé sur l'apprentissage complet (3 498 résidus après exclusion des huit observations d'initialisation), sont soumis aux trois tests. Les degrés de liberté de Ljung-Box sont corrigés (p + q + P + Q = 4).

[[TAB:sarima_diag|Diagnostic des résidus du SARIMA(2,1,1)(0,1,1)[7]|Les trois hypothèses sont rejetées : les résidus sont autocorrélés, à queues épaisses et hétéroscédastiques.]]

| Test | Statistique | p-value |
|---|---|---|
| Ljung-Box, 7 retards | 49,17 | 1,2 × 10⁻¹⁰ |
| Ljung-Box, 14 retards | 72,71 | 1,3 × 10⁻¹¹ |
| Ljung-Box, 28 retards | 110,65 | 4,3 × 10⁻¹³ |
| Jarque-Bera | 3 005,24 | < 10⁻³⁰⁰ |
| ARCH-LM, 7 retards | 304,53 | 6,5 × 10⁻⁶² |

[[FIG:sarima_diag|../figures/arima_sarima/diagnostics_finaux.png|Diagnostic graphique des résidus du SARIMA final|L'ACF des résidus est presque plate (pic résiduel au retard 7), mais le QQ-plot révèle des queues très épaisses et l'écart-type glissant varie fortement selon la saison.]]

L'autocorrélation résiduelle est faible en valeur absolue (pic d'environ 0,10 au retard 7) mais significative vu le nombre d'observations. Le kurtosis des résidus vaut 7,54 (loi normale : 3,00), et la variance dépend nettement de la saison : elle est plus élevée en hiver. **Le modèle est donc retenu comme meilleur candidat prédictif, non comme modèle statistiquement valide** ; ses intervalles gaussiens sont des approximations. L'effet ARCH motive la section 3.3.

### Évaluation externe

Le modèle est réestimé sur les 3 506 jours d'apprentissage puis prévoit les 390 jours de test par blocs de sept jours, à paramètres fixes. Sa **RMSE vaut 82,38 GWh/jour** (MAE 53,12 GWh/jour, MAPE 4,13 %), contre 113,93 pour le naïf saisonnier, soit un gain de 27,69 % de RMSE ; la couverture empirique de l'intervalle nominal à 95 % est de 94,36 %. L'erreur croît avec l'horizon, de 33,83 GWh/jour à h = 1 à 111,38 GWh/jour à h = 7 (annexe A, tableau @tab:annexe_sarima_horizon). Ce gain est descriptif : il n'est pas testé ici ; le test de Diebold–Mariano figure en section 6.

### Limites

La validation interne couvre huit semaines d'été et a servi à des ajustements exploratoires. Le test couvre un seul hiver. Les jours fériés, les températures futures et le cycle annuel ne sont pas modélisés par le SARIMA hebdomadaire ; ils le sont dans les sections suivantes.
