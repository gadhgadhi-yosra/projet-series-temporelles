## 3.2 Modèles multivariés : VAR, causalité de Granger, cointégration et VECM

### Choix des variables et du calendrier

Nous modélisons conjointement la consommation `conso_gwh` et la température moyenne nationale `temp_moy` : la relation chauffage–consommation est le mécanisme principal de la série (section 2.6), et la température doit être prévue par le modèle lui-même puisque la météo future est inconnue. Les deux cycles de la consommation (hebdomadaire et annuel) sont introduits comme **régresseurs exogènes de calendrier connus à l'avance** (six indicatrices de jour de la semaine, le jour férié et trois harmoniques de Fourier annuelles), au lieu de centaines de retards. Ce choix n'introduit pas de fuite d'information, car le calendrier est connu pour le futur, contrairement à la météo.

### Stationnarité et ordre du VAR

L'ADF et le KPSS (tableau @tab:stationnarite) concluent à la stationnarité en niveau des deux séries (consommation : ADF p = 0,001, KPSS p = 0,076, cas limite ; température : ADF p = 0,009). Le VAR est donc estimé **en niveaux**. Les critères d'information, calculés sur l'échantillon d'estimation (3 450 jours) pour laisser la validation interne vierge, proposent p = 3 (BIC), p = 9 (HQIC) et p = 13 (AIC et FPE) ; le gain d'AIC est considérable de p = 1 à p = 3 (7,645 à 7,441) puis négligeable (7,409 à p = 13). Nous départageons ces trois ordres par la règle commune au groupe, la RMSE minimale en validation interne.

[[TAB:var_ordre|Choix de l'ordre du VAR|Les trois ordres sont presque équivalents en validation ; la règle retient VAR(3), le plus parcimonieux.]]

| Ordre p | Critère d'origine | RMSE de validation (GWh/jour) | MAE de validation (GWh/jour) |
|---|---|---|---|
| 3 | BIC | 48,37 | 38,66 |
| 9 | HQIC | 48,53 | 36,43 |
| 13 | AIC, FPE | 48,74 | 37,50 |

Le VAR(3) final, réestimé sur les 3 506 jours d'apprentissage, est stable : le module maximal des valeurs propres de sa matrice compagne vaut 0,87, inférieur à 1.

### Diagnostic des résidus

[[TAB:var_diag|Diagnostic des résidus du VAR(3)|Les résidus de la température sont proches d'un bruit blanc ; ceux de la consommation sont autocorrélés, à queues épaisses et hétéroscédastiques.]]

| Équation | Ljung-Box (p, 7 retards) | Jarque-Bera (p) | Kurtosis | ARCH-LM (p) |
|---|---|---|---|---|
| Consommation | < 10⁻³⁰ | < 10⁻²⁰⁰ | 5,79 | 10⁻³² |
| Température | 0,129 | 10⁻⁹ | 3,48 | 6 × 10⁻⁴ |

Les tests multivariés concluent de même (portmanteau à 14 retards : p ≈ 10⁻⁴⁹). Les défauts de l'équation de consommation (autocorrélation aux retards 1 et 7, variance non constante) motivent la modélisation de la variance en section 3.3 et imposent de la prudence sur les intervalles gaussiens.

### Causalité au sens de Granger

[[TAB:granger|Tests de causalité de Granger|La température cause la consommation de façon très nette ; le sens inverse, statistiquement significatif, est 18 fois plus faible et n'a pas de sens physique.]]

| Hypothèse | Statistique F | p-value |
|---|---|---|
| Température → consommation | 118,57 | 7 × 10⁻⁷⁵ |
| Consommation → température | 6,61 | 1,9 × 10⁻⁴ |

La température cause la consommation au sens de Granger quel que soit l'ordre testé (p < 10⁻³⁴ de p = 1 à 13). Le sens inverse est aussi significatif, mais sa statistique est 18 fois plus faible et sa p-value varie de 0,026 à 5 × 10⁻⁵ selon l'ordre ; la consommation ne détermine pas la météo, et ce résultat est probablement un artefact (la température nationale moyenne mesure imparfaitement la météo ressentie, et le test est très puissant avec 3 506 observations). Granger mesure une causalité **prédictive**, non physique ; les chocs du même jour sont corrélés à −0,46.

### Réponse impulsionnelle

[[FIG:irf|../figures/ghada/var_irf_temp_conso.png|Réponse de la consommation à un choc de température|Un choc de +1 écart-type (environ 1,25 °C) réduit la consommation de 17 GWh/jour le jour même et de 29 GWh/jour au pic, puis l'effet décroît lentement.]]

Avec la température ordonnée en premier (un choc de consommation ne change pas la météo du jour), un choc de température de +1 écart-type (environ 1,25 °C) réduit la consommation de 17 GWh/jour le jour même, de 29 GWh/jour au pic (jours 1 et 2) et de 14,5 GWh/jour au jour 7, soit environ −24 GWh/jour par °C de choc. Cet effet moyen sur l'année est plus faible que la pente hivernale de la section 2.6 (56 GWh/jour par °C sous 15 °C), car il inclut l'été, sans chauffage.

### Cointégration (Johansen) et VECM

Le test de Johansen (constante, deux retards en différences choisis par le BIC) rejette r ≤ 0 (statistique de la trace 337,72 contre un seuil à 95 % de 15,49) et r ≤ 1 (39,55 contre 3,84) : **le rang est 2, le rang plein**. Le résultat est identique avec 1 à 13 retards, avec constante ou tendance, et sur des séries corrigées du calendrier ; seule la spécification sans constante sur les données brutes, inadaptée (consommation moyenne de 1 254 GWh/jour), donne r = 1. Un rang plein signifie que les deux séries sont **déjà stationnaires** : il n'y a pas de tendance stochastique commune, donc pas de cointégration au sens strict, et un VAR en niveaux est la spécification cohérente.

Comme le sujet demande un VECM, nous l'estimons avec r = 1 **imposé**, en signalant que ce choix n'est pas soutenu par le test. Le nombre de retards en différences est choisi parmi 2, 8 et 12 (ordres du BIC, du HQIC et de l'AIC) par la même règle de validation interne (RMSE de 55,48, 62,37 et 53,44 GWh/jour) : **VECM(k = 12, r = 1)**. La relation d'équilibre est conso + 82,08 × température = constante. La **vitesse de correction** est α = −0,0181 (p = 0,004) : environ 1,8 % de l'écart à l'équilibre est résorbé chaque jour, soit une demi-vie d'environ 38 jours. Cette valeur n'est pas robuste : selon le nombre de retards, α vaut −0,052 (demi-vie de 13 jours), +0,007 (aucune correction) ou −0,018 (annexe A, tableau @tab:annexe_vecm), et β varie du simple au double (de 61,8 à 134,1). Nous ne la lisons que comme un ordre de grandeur. Les résidus du VECM présentent les mêmes défauts que ceux du VAR (Ljung-Box p ≈ 10⁻¹⁶ et ARCH-LM p ≈ 10⁻²⁶ pour la consommation).

### Performance sur le test externe

Sur les 390 jours de test, par blocs de sept jours, le **VAR(3) obtient une RMSE de 78,96 GWh/jour** (MAE 54,67 GWh/jour, MAPE 4,31 %), avec une couverture de 93,1 % de l'intervalle nominal à 95 %. Le **VECM** est moins précis (RMSE 87,56 GWh/jour, MAE 58,71 GWh/jour, MAPE 4,61 %, couverture 91,3 %) : imposer une relation de cointégration que les données ne soutiennent pas contraint le modèle sans bénéfice. L'avantage apparent du VAR sur le SARIMA (82,38) peut venir en partie du calendrier que le SARIMA n'inclut pas ; l'écart n'est pas significatif (section 6).

### Limites

Le VAR(3) n'a pas les retards hebdomadaires 7 et 8 que l'AR creux de la section 3.3 exploite. Ses intervalles sont gaussiens et ignorent l'incertitude sur les paramètres. Le VECM suppose des séries I(1) cointégrées, hypothèse contredite par les tests : son interprétation (équilibre, vitesse de correction) est donc fragile. Pour une véritable question de cointégration, il faudrait des variables non stationnaires (niveaux de prix de l'énergie, production cumulée), hors du périmètre de ce projet.
