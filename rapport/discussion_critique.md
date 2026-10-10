# Discussion critique — modèles multivariés, GARCH et Prophet

Texte préparé avec assistance IA à partir des calculs du projet, le 9 octobre 2026. Cette discussion porte sur les sections 3.2, 3.3 et 4.3 ; elle devra être complétée avec les résultats de 3.1, 4.1, 4.2 et 6 une fois ceux-ci livrés.

## Synthèse chiffrée (test externe, 390 jours, blocs de 7 jours)

| Modèle | RMSE (GWh) | MAE | MAPE (%) | Couverture 95 % |
| --- | --- | --- | --- | --- |
| AR creux, variance constante (témoin) | 74,06 | 49,16 | 3,84 | 93,3 % |
| AR-GARCH(1,2)-t | 74,45 | 48,61 | 3,78 | 95,9 % |
| VAR(3) | 78,96 | 54,67 | 4,31 | 93,1 % |
| SARIMA(2,1,1)(0,1,1)[7] (Yosra) | 82,38 | 53,12 | 4,13 | 94,4 % |
| VECM(k = 12, r = 1) | 87,56 | 58,71 | 4,61 | 91,3 % |
| Prophet (ré-ajusté chaque semaine) | 101,85 | 75,27 | 5,93 | 88,5 % |
| Naïf dernière valeur | 109,13 | 76,63 | 6,46 | — |
| Naïf saisonnier | 113,93 | 76,66 | 5,97 | — |

À h = 1, tous les modèles dynamiques sont à égalité (33–38 GWh) : la persistance suffit. L'erreur croît ensuite jusqu'à 96–111 GWh à h = 7, et l'avantage des modèles AR apparaît à partir de h = 4.

## Ce que les résultats montrent

1. **Le calendrier compte probablement autant que le choix du modèle.** Les modèles de ce notebook utilisent le jour férié et un cycle annuel que le SARIMA n'a pas. Le témoin (AR avec calendrier, sans GARCH) fait aussi bien que le meilleur modèle : une part importante du gain vient vraisemblablement de l'information de calendrier et d'une moyenne bien choisie (retards 1, 2, 7, 8), plutôt que de la sophistication du modèle. Nous n'avons pas isolé l'effet du calendrier par une expérience dédiée (par exemple un SARIMA avec les mêmes régresseurs) ; c'est une hypothèse, pas un résultat.
2. **Le GARCH sert à quantifier l'incertitude, pas à prévoir la moyenne.** Il améliore la couverture des intervalles (95,9 % contre 93,3 %) mais pas la RMSE.
3. **La température explique beaucoup la consommation (Granger, IRF), mais le VAR(3) prévoit moins bien (78,96) que l'AR creux avec calendrier (74,06).** Deux explications possibles, non départagées ici : sans météo future, la température prévue par le VAR apporte peu à 7 jours ; et le VAR(3) n'a pas les retards hebdomadaires 7 et 8 que l'AR creux exploite. Une prévision météo externe changerait peut-être ce résultat ; nous ne l'avons pas utilisée.
4. **Le VECM n'est pas adapté à ces données.** Johansen conclut à un rang plein : les deux séries sont stationnaires. Le VECM imposé à r = 1 est moins précis que le VAR et sa vitesse de correction n'est pas robuste (de 13 jours à aucune correction selon le nombre de retards).
5. **Prophet est le moins adapté à la prévision à 7 jours**, faute de mémoire à court terme ; il est utile pour décrire tendance et saisonnalités.

## Limites méthodologiques

- **Diagnostics défavorables.** Tous les modèles laissent des résidus non normaux ; VAR, VECM et Prophet gardent de l'hétéroscédasticité (que seul le GARCH traite) et le VAR, le VECM et Prophet gardent aussi de l'autocorrélation. Les intervalles gaussiens sont des approximations. Le diagnostic « obligatoire » est rempli (Ljung-Box, normalité, ARCH-LM) mais il ne valide pas les hypothèses, il les contredit.
- **GARCH quasi-intégré.** Une persistance α+β ≈ 1 indique que la composante saisonnière de la variance n'est pas modélisée explicitement. Des pistes : variance saisonnière (indicatrices d'hiver), GJR-GARCH pour une réponse asymétrique, ou régimes de volatilité.
- **Protocole.** Un seul découpage chronologique, un test de 390 jours (une seule année : une vague de froid ou de chaleur exceptionnelle peut dominer les erreurs). La sélection en validation interne (8 semaines d'été) est peu représentative de l'hiver. Les ordres du VAR sont choisis sur un échantillon dont l'EDA avait déjà vu les données.
- **Écarts non testés.** Les différences entre modèles voisins (par exemple 74,1 contre 79,0) ne sont pas testées statistiquement dans cette partie ; le test de Diebold-Mariano (section 6) est nécessaire avant toute affirmation de supériorité.
- **Paramètres fixes.** Les paramètres ne sont jamais ré-estimés pendant le test (sauf Prophet) : sur une année avec ruptures possibles, une ré-estimation régulière pourrait aider.
- **Reproductibilité.** Notebook testé avec les versions listées en tête ; avec d'autres versions de `statsmodels`/`arch`, de petites différences numériques sont possibles (optimiseurs).

## Pistes d'amélioration

Intégrer une prévision météo externe pour le VAR ; inclure les retards hebdomadaires (7, 8) directement dans le VAR ; modéliser la variance saisonnière ; combiner les prévisions (moyenne AR-GARCH/VAR/SARIMA) ; utiliser un hybride (SARIMA + réseau de neurones sur les résidus, section 4.2).
