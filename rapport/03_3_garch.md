## 3.3 Modèles de volatilité conditionnelle : ARCH et GARCH

### Effet ARCH dans les résidus

Le test ARCH-LM (7 retards) rejette l'homoscédasticité des résidus de tous les modèles précédents : SARIMA (p = 6,5 × 10⁻⁶²), équation de consommation du VAR (p ≈ 10⁻³²) et du VECM (p ≈ 10⁻²⁶). Les erreurs sont plus fortes en hiver (vagues de froid), ce qui justifie un modèle de variance conditionnelle σ²ₜ = ω + α ε²ₜ₋₁ + β σ²ₜ₋₁.

### Construction du modèle

Comme la série est une consommation et non un rendement financier, nous modélisons les **écarts à la saisonnalité** : (1) nous retirons la saisonnalité par régression sur le calendrier (Fourier annuel, jour de la semaine, jour férié), estimée sur l'apprentissage (R² = 0,823 ; écart-type des écarts 106 GWh/jour) ; (2) les écarts ont une variance non constante (ARCH-LM p ≈ 0) ; (3) la PACF présente des pics aux retards 1, 2, 7 et 8, et le meilleur BIC est obtenu par un **AR creux sur les retards 1, 2, 7, 8 et 14** (BIC 35 533,90), meilleur que AR(14) (35 597,80) et AR(21) (35 565,40) ; (4) un GARCH est estimé sur les résidus de cette moyenne, avec une loi normale puis une loi de Student.

[[TAB:garch_comparaison|Comparaison de GARCH(1,1) et d'ordres supérieurs|La loi de Student améliore massivement l'ajustement ; GARCH(1,2)-t a le meilleur BIC ; GARCH(2,1) n'apporte rien par rapport à GARCH(1,1).]]

| Modèle | Log-vraisemblance | BIC | Persistance α + β |
|---|---|---|---|
| GARCH(1,1), loi normale | −1 145,45 | 2 364,32 | 1,00 |
| GARCH(2,1), loi normale | −1 145,45 | 2 372,48 | 1,00 |
| GARCH(1,2), loi normale | −1 133,77 | 2 349,13 | 0,99 |
| GARCH(1,1), loi de Student | −873,83 | 1 829,24 | 1,00 |
| GARCH(2,1), loi de Student | −873,83 | 1 837,39 | 1,00 |
| **GARCH(1,2), loi de Student** | **−857,36** | **1 804,47** | 1,00 |

Le GARCH(1,1) est le modèle de référence demandé ; l'ordre (1,2) gagne 16,46 points de log-vraisemblance pour un seul paramètre supplémentaire, et la loi de Student (ν ≈ 4,10) traduit des queues très épaisses. Nous retenons **AR-GARCH(1,2)-t** (α₁ = 0,34 ; β₁ = 0,18 ; β₂ = 0,49). La persistance proche de 1 (quasi-IGARCH) reflète sans doute une volatilité saisonnière et par régimes que le modèle traduit par une mémoire extrême : c'est une limite.

### Diagnostic des résidus standardisés

[[TAB:garch_diag|Résidus standardisés du GARCH|Le GARCH(1,2)-t est le seul à rendre les résidus standardisés homoscédastiques à 5 % (p = 0,050 et 0,060) ; le GARCH(1,1) n'y parvient pas.]]

| Modèle | Ljung-Box sur z (p, 7 retards) | Ljung-Box sur z² (p, 7 retards) | ARCH-LM sur z (p) |
|---|---|---|---|
| AR creux, variance constante (témoin) | 0,85 | 3 × 10⁻¹¹⁶ | 2 × 10⁻⁸⁵ |
| AR-GARCH(1,1), loi de Student | 0,59 | 2 × 10⁻⁵ | 4 × 10⁻⁵ |
| **AR-GARCH(1,2), loi de Student** | 0,72 | 0,050 | 0,060 |

La moyenne est bien spécifiée (plus d'autocorrélation) et l'effet ARCH est presque entièrement capté par le (1,2)-t, mais le test de Jarque-Bera rejette encore la normalité des résidus standardisés (kurtosis 10,10) : même une loi de Student n'absorbe pas tous les jours extrêmes. Les p-values à la limite du seuil (0,050 et 0,060) ne valident pas l'hypothèse d'homoscédasticité ; elles indiquent seulement qu'on ne la rejette plus à 5 %.

### Volatilité conditionnelle et événements connus

Le notebook ne sauvegardait pas la série de la volatilité conditionnelle σₜ ; nous l'avons recalculée avec la même spécification (script `scripts/garch_volatilite.py`, résultats dans `exports/garch_volatilite_conditionnelle.csv`) et retrouvé la log-vraisemblance de −857,36. La médiane de σₜ sur l'apprentissage est de 31,78 GWh/jour.

[[FIG:volatilite|../figures/ghada/garch_volatilite_evenements.png|Volatilité conditionnelle de l'AR-GARCH(1,2)-t et événements|La volatilité est maximale en hiver et culmine en décembre 2022 ; les épisodes de froid de 2017, 2018 et 2021 et l'hiver de sobriété sont bien en hausse, le confinement l'est moins.]]

[[TAB:garch_evenements|Volatilité conditionnelle moyenne pendant les événements documentés|Pendant les vagues de froid et l'hiver 2022-23, le maximum de la volatilité atteint de 2,69 à 4,55 fois sa médiane ; pendant le confinement, il ne la double que brièvement (2,18 fois).]]

| Événement | Période | σ moyen (GWh/jour) | σ maximal (GWh/jour) | Date du maximum | Maximum / médiane |
|---|---|---|---|---|---|
| Vague de froid de janvier 2017 | 1–31 janvier 2017 | 71,93 | 122,65 | 3 janvier 2017 | 3,86 |
| Vague de froid « Moscou-Paris » | 20 février – 5 mars 2018 | 72,76 | 99,40 | 27 février 2018 | 3,13 |
| Premier confinement | 17 mars – 10 mai 2020 | 40,00 | 69,26 | 24 mars 2020 | 2,18 |
| Vague de froid de janvier 2021 | 1–31 janvier 2021 | 57,38 | 85,47 | 18 janvier 2021 | 2,69 |
| Hiver 2022-23 (sobriété) | 1er décembre 2022 – 31 janvier 2023 | 61,20 | 144,50 | 20 décembre 2022 | 4,55 |

La plus forte valeur de la série (144,50 GWh/jour le 20 décembre 2022) tombe dans l'hiver de sobriété. Les trois vagues de froid font passer la volatilité moyenne de la médiane (31,78) à 57,38–72,76 GWh/jour. Le premier confinement ne la fait monter qu'à 40,00 GWh/jour en moyenne, avec un pic à 69,26 GWh/jour le 24 mars 2020, au début de la mesure : le choc a été brutal mais court. **Le lien est partiel** : parmi les dix plus fortes valeurs (espacées d'au moins 30 jours, `exports/garch_pics_volatilite.csv`), une seule tombe dans les événements documentés (20 décembre 2022). Les autres (17 août 2021, 27 décembre 2016, 3 novembre 2020, 6 janvier 2025, 3 mai 2016, 27 décembre 2021, 16 juillet 2024, 17 août 2020, 2 avril 2022) ne sont pas expliquées par ces événements ; plusieurs tombent à la fin décembre ou à la mi-août, périodes où le calendrier est atypique, sans que nous l'ayons vérifié.

### Prévision

Sur le test externe, **AR-GARCH(1,2)-t obtient une RMSE de 74,45 GWh/jour** (MAE 48,61 GWh/jour, MAPE 3,78 %) et une couverture de 95,9 % de l'intervalle nominal à 95 % (largeur moyenne 300 GWh/jour). Le témoin à variance constante obtient une RMSE de 74,06 GWh/jour (MAE 49,16 GWh/jour) et une couverture de 93,3 % (largeur 286 GWh/jour). **Le GARCH n'améliore donc pas la prévision ponctuelle** : c'est la moyenne autorégressive avec calendrier qui fait le travail. Il **calibre mieux les intervalles** (95,9 % contre 93,3 % pour un niveau nominal de 95 %).

### Limites

La persistance proche de 1 signale que la composante saisonnière de la variance n'est pas modélisée explicitement. Des pistes non évaluées : variance saisonnière (indicatrices d'hiver), GJR-GARCH pour une réponse asymétrique, régimes de volatilité.
