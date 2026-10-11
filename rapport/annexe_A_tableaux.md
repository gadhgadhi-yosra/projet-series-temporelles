# Annexe A — Tableaux détaillés

## A.1 Candidats SARIMA sur la validation interne

[[TAB:annexe_sarima|Quinze modèles comparés sur la validation interne (3 450 jours d'estimation, huit blocs de sept jours)|Les AIC et BIC sont donnés à titre informatif : on ne les compare pas entre différenciations différentes.]]

| Modèle | RMSE (GWh/jour) | MAE (GWh/jour) | AIC | BIC |
|---|---|---|---|---|
| SARIMA(2,1,1)(0,1,1)[7] | 42,67 | 32,60 | 35 807,95 | 35 838,67 |
| SARIMA(2,1,2)(0,1,1)[7] | 42,81 | 32,74 | 35 808,26 | 35 845,12 |
| SARIMA(1,1,0)(0,1,1)[7] | 42,97 | 31,11 | 35 876,30 | 35 894,74 |
| SARIMA(1,1,0)(1,0,1)[7] | 43,01 | 31,14 | 35 957,99 | 35 982,58 |
| SARIMA(0,1,1)(0,1,1)[7] | 43,05 | 30,99 | 35 860,60 | 35 879,03 |
| SARIMA(1,1,0)(1,1,1)[7] | 43,25 | 32,09 | 35 906,24 | 35 930,81 |
| SARIMA(1,1,1)(0,1,1)[7] | 43,37 | 31,12 | 35 859,82 | 35 884,40 |
| SARIMA(3,1,1)(0,1,1)[7] | 43,47 | 33,84 | 35 886,94 | 35 923,80 |
| SARIMA(1,0,0)(1,0,1)[7] | 47,25 | 34,38 | 36 058,09 | 36 088,82 |
| `auto_arima` saisonnier : SARIMA(2,1,1)(1,0,0)[7] | 48,10 | 36,83 | 37 145,48 | 37 176,21 |
| Naïf saisonnier | 55,22 | 44,04 | — | — |
| `auto_arima` non saisonnier : ARIMA(2,1,2) | 74,23 | 59,01 | 39 583,83 | 39 614,56 |
| Naïf « dernière valeur » | 88,59 | 67,73 | — | — |
| ARIMA(1,1,0) | 88,92 | 67,68 | 40 355,59 | 40 367,88 |
| ARIMA(0,1,1) | 89,21 | 67,84 | 40 236,05 | 40 248,34 |

## A.2 SARIMA retenu : erreurs selon l'horizon

[[TAB:annexe_sarima_horizon|Erreurs du SARIMA(2,1,1)(0,1,1)[7] selon l'horizon sur le test externe|L'erreur croît avec l'horizon ; les horizons 6 et 7 ont une observation de moins car le dernier bloc compte cinq jours.]]

| Horizon (jours) | Observations | RMSE (GWh/jour) | MAE (GWh/jour) | Biais (GWh/jour) | Couverture à 95 % | Largeur moyenne de l'intervalle (GWh/jour) |
|---|---|---|---|---|---|---|
| 1 | 56 | 33,83 | 22,99 | −0,84 | 96,4 % | 170,46 |
| 2 | 56 | 60,66 | 41,77 | 5,18 | 94,6 % | 262,95 |
| 3 | 56 | 72,48 | 51,30 | 3,73 | 98,2 % | 326,09 |
| 4 | 56 | 82,46 | 59,32 | −2,34 | 91,1 % | 371,70 |
| 5 | 56 | 90,30 | 60,41 | −3,24 | 96,4 % | 406,59 |
| 6 | 55 | 101,16 | 64,80 | 6,90 | 92,7 % | 434,70 |
| 7 | 55 | 111,38 | 71,76 | −0,59 | 90,9 % | 458,32 |

## A.3 VECM : robustesse de la vitesse de correction

[[TAB:annexe_vecm|Vitesse de correction du VECM selon le nombre de retards en différences|La vitesse de correction change de signe et β varie du simple au double : elle n'est lisible que comme un ordre de grandeur.]]

| Retards en différences k | α (consommation) | p-value de α | α (température) | β (température) | Demi-vie (jours) |
|---|---|---|---|---|---|
| 2 | −0,052 | < 0,001 | −0,0026 | 61,8 | 12,9 |
| 8 | 0,007 | 0,028 | −0,0017 | 134,1 | aucune correction |
| 12 | −0,018 | 0,004 | −0,0023 | 82,1 | 37,9 |

## A.4 Réplication R et Python : les 27 éléments comparés

[[TAB:annexe_r|Comparaison R et Python, 27 éléments|25 éléments sur 27 coïncident à 0,1 % près ; les deux écarts supérieurs concernent le GARCH.]]

| Élément | Python | R | Écart relatif |
|---|---|---|---|
| ADF consommation (brute) | −4,101 | −4,101 | 0,00 % |
| KPSS consommation (brute) | 0,403 | 0,403 | 0,00 % |
| SARIMA retenu : RMSE test | 82,382 | 82,377 | 0,01 % |
| SARIMA : couverture 95 % | 0,944 | 0,944 | 0,00 % |
| ADF température | −3,478 | −3,478 | 0,00 % |
| Ordre VAR (BIC / AIC) | 3,000 | 3,000 | 0,00 % |
| VAR(3) : RMSE validation | 48,366 | 48,366 | 0,00 % |
| Granger temp → conso (F) | 118,573 | 118,573 | 0,00 % |
| Granger conso → temp (F) | 6,606 | 6,606 | 0,00 % |
| Causalité instantanée (chi2) | 618,100 | 618,050 | 0,01 % |
| IRF : pic de réponse (GWh, jour 1) | −29,400 | −29,399 | 0,00 % |
| Johansen trace r = 0 | 337,720 | 337,716 | 0,00 % |
| Johansen trace r ≤ 1 | 39,550 | 39,551 | 0,00 % |
| VECM β_temp | 82,078 | 82,078 | 0,00 % |
| VECM α_conso | −0,018 | −0,018 | 0,07 % |
| VECM demi-vie (jours) | 37,900 | 37,923 | 0,06 % |
| VAR : RMSE test | 78,957 | 78,957 | 0,00 % |
| VAR : couverture 95 % | 0,931 | 0,931 | 0,02 % |
| VECM : RMSE test | 87,562 | 87,562 | 0,00 % |
| VECM : couverture 95 % | 0,913 | 0,913 | 0,02 % |
| BIC de l'AR[1,2,7,8,14] | 35 533,900 | 35 533,900 | 0,00 % |
| GARCH α1 | 0,337 | 0,336 | 0,35 % |
| GARCH β1 + β2 | 0,663 | 0,663 | 0,03 % |
| GARCH ν (Student) | 4,099 | 4,097 | 0,04 % |
| AR-GARCH : RMSE test | 74,453 | 74,443 | 0,01 % |
| AR-GARCH : couverture 95 % | 0,959 | 0,956 | 0,27 % |
| Témoin : RMSE test | 74,062 | 74,062 | 0,00 % |

## A.5 Corrélation température–consommation selon le mois

[[TAB:annexe_profil|Corrélation selon le mois, sur les niveaux et sur les variations journalières|Les deux colonnes ont la même forme : le lien saisonnier n'est pas une coïncidence de calendrier.]]

| Mois | Corrélation sur les niveaux | Corrélation sur les variations |
|---|---|---|
| janvier | −0,92 | −0,68 |
| février | −0,88 | −0,77 |
| mars | −0,91 | −0,80 |
| avril | −0,91 | −0,81 |
| mai | −0,89 | −0,69 |
| juin | −0,85 | −0,49 |
| juillet | −0,41 | −0,09 |
| août | 0,31 | 0,26 |
| septembre | 0,34 | 0,36 |
| octobre | −0,40 | 0,19 |
| novembre | −0,83 | −0,21 |
| décembre | −0,93 | −0,57 |

## A.6 Sensibilité à la température de chaque hiver

[[TAB:annexe_hivers|Corrélation, pente et consommation estimée à 8 °C pour chaque hiver|La pente reste comprise entre −40,2 et −56,5 GWh/jour par °C, tandis que le niveau à 8 °C baisse après l'hiver 2021-2022.]]

| Hiver | Jours | Corrélation | Pente (GWh/jour par °C) | Consommation à 8 °C (GWh/jour) |
|---|---|---|---|---|
| 2016-2017 | 151 | −0,924 | −50,8 | 1 557 |
| 2017-2018 | 151 | −0,903 | −44,9 | 1 575 |
| 2018-2019 | 151 | −0,883 | −47,8 | 1 548 |
| 2019-2020 | 152 | −0,675 | −40,2 | 1 513 |
| 2020-2021 | 151 | −0,898 | −46,3 | 1 506 |
| 2021-2022 | 151 | −0,936 | −56,5 | 1 524 |
| 2022-2023 | 151 | −0,950 | −50,1 | 1 424 |
| 2023-2024 | 152 | −0,921 | −47,8 | 1 450 |
| 2024-2025 | 151 | −0,910 | −48,2 | 1 453 |
| 2025-2026 | 151 | −0,890 | −45,0 | 1 469 |

## A.7 RMSE par horizon pour les dix modèles

[[TAB:annexe_horizon|RMSE selon l'horizon de prévision (GWh/jour)|Les modèles dynamiques sont à égalité à l'horizon 1 ; Prophet est mauvais dès l'horizon 1.]]

| Horizon (jours) | AR-GARCH(1,2)-t | LSTM | GRU | VAR(3) | SARIMA + LSTM | SARIMA | VECM(12, r=1) | Prophet | Persistance | Naïf saisonnier |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 37,9 | 32,7 | 31,8 | 33,4 | 34,6 | 33,8 | 34,2 | 99,6 | 35,8 | 106,0 |
| 2 | 52,6 | 52,1 | 51,6 | 59,2 | 57,8 | 60,7 | 62,7 | 96,4 | 62,9 | 113,0 |
| 3 | 73,6 | 70,8 | 71,0 | 79,6 | 71,6 | 72,5 | 86,4 | 105,8 | 129,9 | 119,0 |
| 4 | 78,3 | 80,9 | 84,9 | 86,5 | 80,2 | 82,5 | 97,5 | 102,9 | 165,1 | 118,6 |
| 5 | 76,0 | 76,5 | 78,0 | 80,8 | 81,9 | 90,3 | 94,2 | 96,4 | 96,5 | 111,0 |
| 6 | 90,2 | 90,1 | 91,7 | 93,8 | 98,5 | 101,2 | 102,7 | 104,0 | 106,3 | 113,6 |
| 7 | 96,2 | 101,3 | 102,9 | 100,0 | 111,3 | 111,4 | 111,0 | 106,9 | 115,8 | 115,8 |

## A.8 Prévisions du 1er au 7 septembre 2026 avec intervalles à 95 %

[[TAB:annexe_intervalles|Prévisions et intervalles nominaux à 95 % (GWh/jour)|Le 1er septembre, l'intervalle d'AR-GARCH est le plus étroit et celui de Prophet le plus large ; tous sont nominaux et ne garantissent pas la couverture future.]]

| Date | SARIMA | AR-GARCH | VAR(3) | VECM | Prophet |
|---|---|---|---|---|---|
| 1er septembre | 1 086,54 [1 002,32 ; 1 170,76] | 1 079,10 [1 030,19 ; 1 128,01] | 1 097,54 [1 024,67 ; 1 170,40] | 1 100,64 [1 027,94 ; 1 173,34] | 1 090,11 [905,85 ; 1 256,13] |
| 2 septembre | 1 090,60 [960,47 ; 1 220,73] | 1 082,29 [1 004,74 ; 1 159,84] | 1 102,98 [991,52 ; 1 214,44] | 1 110,17 [996,53 ; 1 223,82] | 1 094,77 [928,70 ; 1 261,98] |
| 3 septembre | 1 085,84 [924,27 ; 1 247,41] | 1 082,22 [985,06 ; 1 179,38] | 1 099,00 [963,81 ; 1 234,19] | 1 108,48 [968,81 ; 1 248,15] | 1 094,20 [924,75 ; 1 263,28] |
| 4 septembre | 1 074,40 [890,09 ; 1 258,72] | 1 064,36 [953,10 ; 1 175,61] | 1 083,43 [933,27 ; 1 233,59] | 1 086,69 [928,59 ; 1 244,80] | 1 080,21 [910,60 ; 1 268,07] |
| 5 septembre | 977,91 [776,18 ; 1 179,65] | 954,01 [832,24 ; 1 075,79] | 973,08 [812,76 ; 1 133,40] | 977,74 [805,87 ; 1 149,62] | 972,48 [806,24 ; 1 138,89] |
| 6 septembre | 938,23 [722,48 ; 1 153,98] | 906,98 [776,98 ; 1 036,98] | 923,66 [756,02 ; 1 091,29] | 933,00 [750,61 ; 1 115,40] | 925,55 [766,44 ; 1 080,79] |
| 7 septembre | 1 056,45 [828,94 ; 1 283,96] | 1 049,73 [913,05 ; 1 186,42] | 1 067,23 [894,17 ; 1 240,30] | 1 071,65 [880,09 ; 1 263,21] | 1 071,15 [899,87 ; 1 233,29] |

## A.9 Paires significatives en perte absolue seulement

[[TAB:annexe_dm_abs|Dix paires significatives après correction de Holm en perte absolue seulement|Elles opposent toutes un modèle dynamique au naïf saisonnier, à Prophet ou à la persistance ; aucune ne compare deux modèles dynamiques entre eux.]]

| Modèle A (plus petite RMSE) | Modèle B | p corrigée, perte quadratique | p corrigée, perte absolue |
|---|---|---|---|
| AR-GARCH(1,2)-t | Naïf saisonnier | 0,157 | < 0,001 |
| SARIMA | Naïf saisonnier | 0,211 | < 0,001 |
| LSTM | Naïf saisonnier | 0,290 | 0,008 |
| VAR(3) | Prophet | 0,100 | 0,018 |
| SARIMA | Prophet | 0,438 | 0,025 |
| GRU | Naïf saisonnier | 0,380 | 0,032 |
| LSTM | Prophet | 0,554 | 0,032 |
| SARIMA + LSTM | Naïf saisonnier | 0,377 | 0,032 |
| VECM(12, r=1) | Persistance | 0,230 | 0,032 |
| VAR(3) | Naïf saisonnier | 0,391 | 0,040 |

## A.10 Les 45 paires du test de Diebold–Mariano

[[TAB:annexe_dm|Test de Diebold–Mariano sur les 45 paires de modèles|Sept paires sont significatives après correction de Holm en perte quadratique et dix-sept en perte absolue.]]

| Modèle A | Modèle B | p brute, quadratique | p corrigée, quadratique | p brute, absolue | p corrigée, absolue |
|---|---|---|---|---|---|
| AR-GARCH(1,2)-t | LSTM | 0,913 | 1,000 | 0,581 | 1,000 |
| AR-GARCH(1,2)-t | GRU | 0,712 | 1,000 | 0,192 | 1,000 |
| AR-GARCH(1,2)-t | VAR(3) | 0,054 | 1,000 | 0,004 | 0,097 |
| AR-GARCH(1,2)-t | SARIMA + LSTM | 0,265 | 1,000 | 0,120 | 1,000 |
| AR-GARCH(1,2)-t | SARIMA | 0,037 | 0,890 | 0,057 | 1,000 |
| AR-GARCH(1,2)-t | VECM(12, r=1) | 0,036 | 0,890 | 0,002 | 0,053 |
| AR-GARCH(1,2)-t | Prophet | < 0,001 | 0,029 | < 0,001 | < 0,001 |
| AR-GARCH(1,2)-t | Persistance | < 0,001 | < 0,001 | < 0,001 | < 0,001 |
| AR-GARCH(1,2)-t | Naïf saisonnier | 0,004 | 0,157 | < 0,001 | < 0,001 |
| LSTM | GRU | 0,218 | 1,000 | 0,041 | 0,911 |
| LSTM | VAR(3) | 0,576 | 1,000 | 0,308 | 1,000 |
| LSTM | SARIMA + LSTM | 0,228 | 1,000 | 0,208 | 1,000 |
| LSTM | SARIMA | 0,257 | 1,000 | 0,363 | 1,000 |
| LSTM | VECM(12, r=1) | 0,255 | 1,000 | 0,128 | 1,000 |
| LSTM | Prophet | 0,019 | 0,554 | 0,001 | 0,032 |
| LSTM | Persistance | < 0,001 | 0,002 | < 0,001 | < 0,001 |
| LSTM | Naïf saisonnier | 0,009 | 0,290 | < 0,001 | 0,008 |
| GRU | VAR(3) | 0,698 | 1,000 | 0,606 | 1,000 |
| GRU | SARIMA + LSTM | 0,363 | 1,000 | 0,580 | 1,000 |
| GRU | SARIMA | 0,338 | 1,000 | 0,793 | 1,000 |
| GRU | VECM(12, r=1) | 0,293 | 1,000 | 0,240 | 1,000 |
| GRU | Prophet | 0,023 | 0,615 | 0,002 | 0,062 |
| GRU | Persistance | < 0,001 | 0,003 | < 0,001 | < 0,001 |
| GRU | Naïf saisonnier | 0,012 | 0,380 | < 0,001 | 0,032 |
| VAR(3) | SARIMA + LSTM | 0,870 | 1,000 | 0,904 | 1,000 |
| VAR(3) | SARIMA | 0,490 | 1,000 | 0,709 | 1,000 |
| VAR(3) | VECM(12, r=1) | 0,103 | 1,000 | 0,111 | 1,000 |
| VAR(3) | Prophet | 0,003 | 0,100 | < 0,001 | 0,018 |
| VAR(3) | Persistance | < 0,001 | 0,003 | < 0,001 | < 0,001 |
| VAR(3) | Naïf saisonnier | 0,013 | 0,391 | 0,001 | 0,040 |
| SARIMA + LSTM | SARIMA | 0,595 | 1,000 | 0,774 | 1,000 |
| SARIMA + LSTM | VECM(12, r=1) | 0,432 | 1,000 | 0,347 | 1,000 |
| SARIMA + LSTM | Prophet | 0,038 | 0,890 | 0,005 | 0,122 |
| SARIMA + LSTM | Persistance | < 0,001 | < 0,001 | < 0,001 | < 0,001 |
| SARIMA + LSTM | Naïf saisonnier | 0,011 | 0,377 | 0,001 | 0,032 |
| SARIMA | VECM(12, r=1) | 0,403 | 1,000 | 0,157 | 1,000 |
| SARIMA | Prophet | 0,015 | 0,438 | < 0,001 | 0,025 |
| SARIMA | Persistance | < 0,001 | < 0,001 | < 0,001 | < 0,001 |
| SARIMA | Naïf saisonnier | 0,006 | 0,211 | < 0,001 | < 0,001 |
| VECM(12, r=1) | Prophet | 0,020 | 0,554 | 0,005 | 0,122 |
| VECM(12, r=1) | Persistance | 0,007 | 0,230 | 0,001 | 0,032 |
| VECM(12, r=1) | Naïf saisonnier | 0,033 | 0,853 | 0,011 | 0,252 |
| Prophet | Persistance | 0,439 | 1,000 | 0,904 | 1,000 |
| Prophet | Naïf saisonnier | 0,272 | 1,000 | 0,848 | 1,000 |
| Persistance | Naïf saisonnier | 0,647 | 1,000 | 0,970 | 1,000 |

## A.11 Questions de comparaison du sujet

[[TAB:annexe_dm_questions|Tests de Diebold–Mariano pour les comparaisons demandées par le sujet|Aucune de ces différences n'est significative en perte quadratique ; en perte absolue, seule la comparaison du meilleur réseau au naïf saisonnier l'est.]]

| Question | Modèle A | Modèle B | RMSE de A (GWh/jour) | RMSE de B (GWh/jour) | p corrigée, quadratique | p corrigée, absolue |
|---|---|---|---|---|---|---|
| GRU ou LSTM ? | LSTM | GRU | 75,07 | 76,40 | 1,000 | 0,911 |
| Meilleur réseau contre le naïf saisonnier | LSTM | Naïf saisonnier | 75,07 | 113,93 | 0,290 | 0,008 |
| Meilleur réseau contre SARIMA | LSTM | SARIMA | 75,07 | 82,38 | 1,000 | 1,000 |
| Le LSTM améliore-t-il le SARIMA ? | SARIMA + LSTM | SARIMA | 79,92 | 82,38 | 1,000 | 1,000 |
| Hybride contre meilleur réseau seul | LSTM | SARIMA + LSTM | 75,07 | 79,92 | 1,000 | 1,000 |
| VAR contre SARIMA | VAR(3) | SARIMA | 78,96 | 82,38 | 1,000 | 1,000 |
| Meilleur modèle contre son premier concurrent | AR-GARCH(1,2)-t | LSTM | 74,45 | 75,07 | 1,000 | 1,000 |

