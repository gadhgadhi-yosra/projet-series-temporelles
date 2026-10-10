# 4.3 — Modèles additionnels : AR-GARCH et Prophet

Texte préparé avec assistance IA à partir des calculs du projet, le 9 octobre 2026. Résultats reproductibles dans `05_var_vecm_garch_prophet.ipynb`.

## AR-GARCH sur les écarts à la saisonnalité

**Motivation.** Les modèles précédents supposent une variance d'erreur constante. Or les erreurs sont plus fortes l'hiver (vagues de froid) : les tests ARCH-LM rejettent la variance constante pour tous les modèles de 3.1 à 3.3. Un GARCH modélise la variance conditionnelle : σ²_t = ω + α·ε²_{t−1} + β·σ²_{t−1}.

**Construction.** (1) On retire la saisonnalité par régression sur le calendrier (Fourier annuel, jour de semaine, férié), estimée sur l'apprentissage : R² = 0,823, écart-type des écarts 106 GWh. (2) Les écarts ont une variance non constante (ARCH-LM p ≈ 0). (3) Le PACF montre des pics aux retards 1, 2, 7 et 8 ; le meilleur BIC est obtenu par un AR creux [1, 2, 7, 8, 14] (BIC 35 534), meilleur que AR(14) (35 598) et AR(21) (35 565). (4) Un GARCH est estimé sur les résidus de cette moyenne.

**Comparaison GARCH(1,1) et ordres supérieurs** (BIC, apprentissage) :

| Modèle | Log-vraisemblance | BIC | Persistance α+β |
| --- | --- | --- | --- |
| GARCH(1,1), normale | −1 145,5 | 2 364 | 1,000 |
| GARCH(1,2), normale | −1 133,8 | 2 349 | 0,985 |
| GARCH(1,1), Student-t | −873,8 | 1 829 | 1,000 |
| GARCH(2,1), Student-t | −873,8 | 1 837 | 1,000 |
| **GARCH(1,2), Student-t** | **−857,4** | **1 804** | 1,000 |

La loi de Student (ν ≈ 4,1) améliore massivement l'ajustement : les queues sont très épaisses. GARCH(2,1) n'apporte rien par rapport à (1,1), tandis que GARCH(1,2) gagne 16,5 points de log-vraisemblance pour un paramètre. On retient **AR-GARCH(1,2)-t** (α₁ = 0,337 ; β₁ = 0,175 ; β₂ = 0,488). La persistance proche de 1 (quasi-IGARCH) reflète sans doute une volatilité **saisonnière** et par régimes (2020, 2022) que le modèle traduit par une mémoire extrême ; c'est une limite du modèle.

**Résidus standardisés.**

| Modèle | LB(z) p (h = 7) | LB(z²) p (h = 7) | ARCH-LM(z) p |
| --- | --- | --- | --- |
| Moyenne AR, variance constante (témoin) | 0,85 | 10⁻¹¹⁶ | 10⁻⁸⁵ |
| AR-GARCH(1,1), Student-t | 0,59 | 2·10⁻⁵ | 4·10⁻⁵ |
| **AR-GARCH(1,2), Student-t** | 0,72 | 0,050 | 0,060 |

La moyenne est bien spécifiée (plus d'autocorrélation). L'effet ARCH est presque entièrement capté par le (1,2)-t, alors que le (1,1) n'y parvient pas. Jarque-Bera rejette encore la normalité des résidus standardisés (kurtosis ≈ 10).

**Performance sur le test externe.** AR-GARCH(1,2)-t : RMSE 74,45 GWh, MAE 48,61, MAPE 3,78 %, couverture 95,9 % (largeur 300 GWh). Témoin à variance constante : RMSE 74,06, MAE 49,16, couverture 93,3 % (largeur 286 GWh). **Le GARCH n'améliore pas la prévision ponctuelle** (c'est la moyenne AR avec le calendrier qui fait le travail) mais **calibre mieux les intervalles** (95,9 % contre 93,3 % pour un nominal de 95 %). Fichier : `forecasts/garch.csv`.

## Prophet

Prophet décompose la série en tendance linéaire par morceaux, saisonnalités (annuelle, hebdomadaire) et jours fériés (colonne `ferie`). Il n'a pas de terme autorégressif. Hyperparamètres comparés en validation interne : tendance flexible (`changepoint_prior_scale` = 0,5) contre rigide (0,05), mode additif contre multiplicatif. Le meilleur choix est la tendance flexible additive (RMSE de validation 51,6 contre 60,3 pour la tendance rigide), plausiblement parce que la série contient des ruptures (2020, 2022-23). Prophet n'ayant pas d'état à actualiser, il est ré-ajusté toutes les 7 jours sur l'historique disponible.

Les résidus d'apprentissage sont très autocorrélés et hétéroscédastiques (Ljung-Box et ARCH-LM p ≈ 0), ce qui est attendu sans terme autorégressif. Sur le test : **RMSE 101,85 GWh, MAE 75,27, MAPE 5,93 %**, couverture 88,5 % (intervalles trop étroits). Une variante à ajustement unique prévoit directement jusqu'à 390 jours : RMSE 97,81, mais intervalles de 836 GWh de large ; elle n'est pas comparable au protocole h = 7. Prophet fait mieux que les naïfs (109,1 et 113,9) mais moins bien que le SARIMA (82,4). Il reste utile pour lire tendance et saisonnalités (`figures/ghada/prophet_composantes.png`), pas pour la prévision à 7 jours. Fichier : `forecasts/prophet.csv`.
