# 3.2 — Modèle VAR et causalité de Granger

Texte préparé avec assistance IA à partir des calculs du projet, le 9 octobre 2026. Les résultats sont reproductibles dans `05_var_vecm_garch_prophet.ipynb` (tables dans `exports/ghada/`, figures dans `figures/ghada/`). Les données et notebooks de Fayfa ne sont pas modifiés.

## Objectif et choix de modélisation

Un modèle vectoriel autorégressif (VAR) explique chaque variable par ses propres retards et par ceux des autres variables. Nous modélisons conjointement la consommation `conso_gwh` et la température moyenne nationale `temp_moy`, pour deux raisons : la relation chauffage–consommation est le mécanisme principal de la série (corrélation −0,83 avec la température brute, 0,89 avec les degrés-jours, d'après l'EDA de Fayfa), et la température est un signal que le modèle doit prévoir lui-même, puisque la météo future n'est pas connue.

La consommation a deux cycles (hebdomadaire et annuel). Les faire apprendre par des retards demanderait des centaines de paramètres. Ils sont donc introduits comme **régresseurs exogènes de calendrier**, connus à l'avance : six indicatrices de jour de semaine, le jour férié (`ferie`, de Fayfa) et trois harmoniques de Fourier annuelles. Ce n'est pas une fuite d'information : le calendrier est connu pour le futur, contrairement à la météo.

## Stationnarité

Les tests ADF/KPSS sur l'apprentissage concluent à la stationnarité en niveau des deux séries : ADF p = 0,001 (consommation) et 0,009 (température), KPSS p = 0,076 et ≥ 0,10. Le cas de la consommation est limite (KPSS la rejetterait à 10 %). Le VAR est donc estimé en niveaux, sans différenciation.

## Choix de l'ordre

Les critères sont calculés sur l'échantillon d'estimation (3 450 jours) pour garder la validation interne vierge.

| Critère | Ordre retenu |
| --- | --- |
| BIC | 3 |
| HQIC | 9 |
| AIC (et FPE) | 13 |

Le gain d'AIC est considérable de p = 1 à p = 3 (7,645 → 7,441) puis négligeable (7,409 à p = 13). Les trois ordres sont comparés par la règle appliquée à tout le groupe : RMSE minimale en validation interne (8 blocs de 7 jours, paramètres fixes).

| Ordre | RMSE validation (GWh) | MAE validation (GWh) |
| --- | --- | --- |
| 3 | 48,37 | 38,66 |
| 9 | 48,53 | 36,43 |
| 13 | 48,74 | 37,50 |

Les écarts sont minimes. La règle donne **VAR(3)**, qui est aussi l'ordre le plus parcimonieux. Le modèle final est réestimé sur les 3 506 jours d'apprentissage ; il est stable.

## Diagnostics

| Équation | Ljung-Box p (h = 7) | Jarque-Bera p | Kurtosis | ARCH-LM p |
| --- | --- | --- | --- | --- |
| Consommation | 10⁻³⁵ | 10⁻²⁶⁸ | 5,79 | 10⁻³² |
| Température | 0,129 | 10⁻⁹ | 3,48 | 6·10⁻⁴ |

Les résidus de la température sont proches d'un bruit blanc. Ceux de la consommation ne le sont pas : il reste de l'autocorrélation aux retards 1 et 7, les queues sont épaisses et la variance n'est pas constante. Les tests multivariés concluent de même (portmanteau à 14 retards : p ≈ 10⁻⁴⁹). Ces défauts motivent la modélisation de la variance (section 4.3) et imposent de la prudence sur les intervalles gaussiens.

## Causalité de Granger

| Hypothèse | F | p-value |
| --- | --- | --- |
| Température → consommation | 118,6 | 7·10⁻⁷⁵ |
| Consommation → température | 6,6 | 1,9·10⁻⁴ |

La température cause nettement la consommation au sens de Granger, quel que soit l'ordre testé (p < 10⁻³⁴ de p = 1 à 13). Le sens inverse est aussi significatif, mais avec une statistique 18 fois plus faible, et sa p-value varie de 0,026 à 5·10⁻⁵ selon l'ordre. La consommation ne détermine pas la météo : ce résultat est probablement un artefact (hypothèses : la température nationale moyenne mesure imparfaitement la météo ressentie, que la consommation reflète ; le test est très puissant avec 3 506 observations). Granger est une causalité **prédictive**, pas physique. Les chocs du même jour sont corrélés à −0,46.

## Réponse impulsionnelle

Avec la température ordonnée en premier (un choc de consommation ne change pas la météo du jour), un choc de température de +1 σ (≈ 1,25 °C) réduit la consommation de 17 GWh le jour même et de 29 GWh au pic (jours 1–2), soit environ −24 GWh par °C de choc. L'effet décroît lentement (−14,5 GWh au jour 7). Cet effet moyen sur l'année est plus faible que la pente hivernale de l'EDA (≈ 56 GWh/°C sous 15 °C), car il inclut l'été, sans chauffage.

## Performance sur le test externe

Sur les 390 jours de test, évalués par blocs de 7 jours : **RMSE 78,96 GWh, MAE 54,67, MAPE 4,31 %**, couverture de l'intervalle nominal à 95 % de 93,1 % (largeur moyenne 278 GWh). Pour référence, le SARIMA de la section 3.1 obtient une RMSE de 82,38 et le naïf « dernière valeur » 109,13. Les prévisions sont dans `forecasts/var.csv`. Prévision à 7 jours (1er–7 septembre 2026) : `exports/ghada/previsions_7j_var.csv`.

## Limites

Le VAR(3) ne capte pas la structure hebdomadaire fine des résidus (retards 7 et 8, voir 4.3) ; ses résidus sont autocorrélés, non normaux et hétéroscédastiques. Ses intervalles sont gaussiens et ignorent l'incertitude sur les paramètres. L'avantage apparent sur le SARIMA peut venir en partie du calendrier (férié, cycle annuel) que le SARIMA de la section 3.1 n'inclut pas ; l'écart n'est pas testé ici (test de Diebold-Mariano, section 6).
