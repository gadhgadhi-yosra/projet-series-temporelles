# 9 — Conclusion

## 9.1 Ce que le projet établit

**Prévision à 7 jours (sections 3 à 6).** Sur le test (390 jours), AR-GARCH(1,2)-t a la plus petite erreur (RMSE 74,45 GWh/jour), mais aucun test de Diebold–Mariano corrigé (Holm) ne le distingue de SARIMA, LSTM, GRU, VAR(3) ni de l'hybride. SARIMA(2,1,1)(0,1,1)[7] est le modèle retenu par la règle de validation interne ; AR-GARCH est le meilleur observé ; nous ne concluons pas à une supériorité durable. Le témoin « AR à variance constante » (RMSE 74,06 GWh/jour) fait aussi bien : l'essentiel du gain vient d'une moyenne autorégressive avec calendrier, non de la sophistication du modèle. Les huit modèles ont une RMSE inférieure à celle de la persistance (109,13) et du naïf saisonnier (113,93) ; l'écart avec la persistance est significatif en perte quadratique pour six d'entre eux (pas pour le VECM ni Prophet) et l'écart avec le naïf saisonnier ne l'est qu'en perte absolue. La validation croisée temporelle confirme l'avantage des réseaux sur le SARIMA : le GRU est meilleur dans les cinq plis et le LSTM dans quatre, surtout en hiver, sans que cela soit testé statistiquement.

**Contrefactuels (section 7.2).** À météo et calendrier égaux, le premier confinement a réduit la consommation d'environ 8,06 TWh (−12,20 % du 17 mars au 10 mai 2020 ; −13,48 % sur la fenêtre de l'INSEE, contre −14 % publié). La sobriété de l'hiver 2022-23 correspond à −21,96 TWh (−8,27 %) ; la baisse persiste en 2023-24 (−18,95 TWh, −7,19 %) et en 2024-25 (−17,74 TWh, −6,57 %). Une régression indépendante (section 7.1) montre que la consommation de base a baissé d'environ 98 GWh/jour sans changement significatif de la sensibilité au froid (−48,42 contre −47,71 GWh/jour par °C, p = 0,756). Ces effets sont possiblement surestimés d'environ 1 point (biais du modèle en période normale).

**Reproductibilité entre logiciels (section 3.4).** Les analyses statistiques refaites en R donnent les mêmes conclusions que Python : 25 éléments sur 27 sont identiques à 0,1 % près.

## 9.2 Recommandation d'usage

Pour un gestionnaire de réseau qui prévoit la consommation à sept jours, nous recommandons un modèle de type AR-GARCH(1,2)-t (meilleure erreur observée, intervalles les mieux calibrés, interprétable, coût négligeable), avec le SARIMA comme référence statistique et le GRU ou le LSTM comme challengers (section 6.6). Prophet n'est pas adapté à cet horizon.

## 9.3 Limites générales

- **Un seul hiver de test** : les classements entre modèles voisins peuvent changer d'une année à l'autre ; la supériorité observée d'AR-GARCH n'est pas établie statistiquement.
- **Validation courte et estivale** (56 jours), partiellement réutilisée pendant le développement ; la validation croisée temporelle (cinq plis de 56 jours) ne porte que sur les réseaux, le SARIMA et le naïf saisonnier.
- **Pas de météo future** : c'est la principale source d'erreur en hiver. Les modèles qui utilisent le calendrier ont un avantage sur le SARIMA.
- **Protocoles légèrement différents** (Prophet réajusté chaque semaine, hybride pseudo hors échantillon, tests sur 385 jours contre 390 pour les métriques).
- **Diagnostics résiduels défavorables** pour tous les modèles statistiques : les intervalles gaussiens à 95 % sont des approximations, sans garantie de couverture future.
- **Cointégration non soutenue** : le VECM n'est estimé à r = 1 que parce que le sujet le demande.
- **Contrefactuels** : température non pondérée par la population, biais d'environ −1 %, attribution au choc de tout ce que le modèle n'explique pas.
- **Données** : 243 jours consolidés (2026) dans le test ; données brutes absentes du dépôt (le notebook de préparation affiche les adresses de téléchargement).

## 9.4 Prolongements

Évaluer les modèles sur plusieurs hivers ; intégrer une prévision météo externe ; ajouter les mêmes régresseurs de calendrier au SARIMA pour isoler leur effet ; modéliser la variance saisonnière ; combiner les prévisions ; élargir la recherche d'architectures des réseaux avec une validation plus longue ; pondérer la température par la population dans les contrefactuels. Ces pistes ne sont pas évaluées ici.

Les prévisions du 1er au 7 septembre 2026 sont une référence descriptive, non une aide à la décision d'exploitation du réseau : elles reposent sur un seul test, des intervalles approximatifs et aucune donnée météo.
