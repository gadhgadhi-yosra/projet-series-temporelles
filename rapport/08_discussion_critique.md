# 8 — Discussion critique

## 8.1 Ce que les résultats montrent

1. **Le calendrier compte probablement autant que le choix du modèle.** Les modèles des sections 3.2 à 4.3 utilisent le jour férié et un cycle annuel que le SARIMA n'a pas. Le témoin (AR avec calendrier, sans GARCH, RMSE 74,06 GWh/jour) fait aussi bien que le meilleur modèle : une part importante du gain vient vraisemblablement de l'information de calendrier et d'une moyenne bien choisie (retards 1, 2, 7, 8 et 14), plutôt que de la sophistication du modèle. Nous n'avons pas isolé cet effet par une expérience dédiée (par exemple un SARIMA avec les mêmes régresseurs) : c'est une hypothèse, pas un résultat.
2. **Le GARCH sert à quantifier l'incertitude, pas à prévoir la moyenne.** Il améliore la couverture (95,9 % contre 93,3 %) d'intervalles qui restent trop étroits en hiver, pas la RMSE. Son lien avec les événements connus est partiel (section 3.3).
3. **La température explique beaucoup la consommation (Granger, réponse impulsionnelle), mais le VAR(3) prévoit moins bien (78,96 GWh/jour) que l'AR creux avec calendrier (74,06).** Deux explications possibles, non départagées : sans météo future, la température prévue par le VAR apporte peu à sept jours ; et le VAR(3) n'a pas les retards hebdomadaires 7 et 8.
4. **Les réseaux de neurones sont compétitifs sans être meilleurs de façon établie.** Le LSTM (75,07) et le GRU (76,40) se classent juste derrière AR-GARCH sur le test, et battent le SARIMA dans la quasi-totalité des plis de la validation croisée, mais aucune différence n'est significative après correction de Holm. Le calendrier est ce qui les améliore le plus en validation (39,37 contre 46,55 GWh/jour pour le LSTM).
5. **L'hybride apporte un gain faible et ambigu** (RMSE −3,0 % par rapport au SARIMA, MAE et MAPE en légère hausse, différence non significative).
6. **Le VECM n'est pas adapté** : le rang de Johansen est plein et la vitesse de correction n'est pas robuste (de 13 jours à aucune correction selon le nombre de retards).
7. **Prophet est le moins adapté** à la prévision à sept jours parmi les modèles statistiques, faute de mémoire à court terme.
8. **Les résultats ne dépendent pas du logiciel** : la réplication en R reproduit 25 éléments sur 27 à 0,1 % près.

## 8.2 Pourquoi les sensibilités à la température diffèrent

Le rapport cite quatre sensibilités de la consommation à la température : environ **−56 GWh/jour par °C** (section 2.6, pente sous 15 °C), **−48 GWh/jour par °C** (section 7.1, pente d'hiver avant la sobriété), **−24 GWh/jour par °C** (section 3.2, réponse impulsionnelle du VAR) et **−82 GWh/jour par °C** (section 3.2, relation de long terme du VECM). Elles ne mesurent pas la même chose : les deux premières sont des pentes observées par temps froid, sur des échantillons différents (jours sous 15 °C sur toute la période pour −56, jours d'hiver pour −48) ; la réponse impulsionnelle est un effet moyen sur toute l'année, été sans chauffage compris, ce qui l'atténue ; la relation du VECM est imposée avec un rang que le test de Johansen ne soutient pas, et varie du simple au double selon le nombre de retards (de 61,8 à 134,1). Elles ne sont donc pas comparables.

## 8.3 Limites des modèles et du protocole

- **Hypothèses violées.** Tous les modèles laissent des résidus non normaux ; le SARIMA, le VAR, le VECM et Prophet gardent de l'hétéroscédasticité (que seul le GARCH traite), et le VAR, le VECM et Prophet de l'autocorrélation. Le diagnostic demandé est réalisé, mais il contredit les hypothèses ; les intervalles gaussiens sont des approximations.
- **Instabilité des estimations.** La vitesse de correction du VECM change de signe selon le nombre de retards ; la persistance du GARCH proche de 1 traduit une variance saisonnière non modélisée ; les paramètres du GARCH diffèrent légèrement entre `arch` et `rugarch`.
- **Échantillon.** Un seul découpage chronologique et un test de 390 jours, soit un seul hiver : une vague de froid exceptionnelle peut dominer les erreurs. La validation interne (huit semaines d'été) est peu représentative de l'hiver et a été partiellement réutilisée pendant le développement ; les ordres du VAR sont choisis sur un échantillon que l'analyse exploratoire avait déjà vu. La validation croisée temporelle (cinq plis de 56 jours) corrige en partie ce défaut pour les réseaux, le SARIMA et AR-GARCH seulement.
- **Protocoles légèrement différents.** Prophet est réajusté chaque semaine, les autres modèles gardent des paramètres fixes ; l'hybride est pseudo hors échantillon ; les tests de Diebold–Mariano portent sur 385 jours et les métriques sur 390.
- **Tests.** Aucun écart entre modèles dynamiques voisins n'est significatif après Holm ; la perte quadratique est celle des conclusions formelles, et la perte absolue en donne une autre pour dix paires. Les tests asymptotiques sur 55 blocs et la correction sur 45 paires limitent leur puissance.
- **Données.** Les 243 derniers jours (2026) sont des données consolidées, éventuellement révisées. Aucune prévision météo n'est utilisée.
- **Reproductibilité.** Les notebooks ont été exécutés dans des environnements différents (README) ; de petites différences numériques sont possibles.

## 8.4 Avantages et inconvénients de l'IA générative pour l'analyse de séries temporelles en énergie

**Avantages.**
- *Exploration rapide d'hypothèses* : à partir de statistiques descriptives, un LLM peut proposer des familles de modèles et des diagnostics à envisager, ce qui accélère la phase de cadrage et rappelle des pistes oubliées.
- *Vulgarisation et communication* : reformuler des résultats (erreur, intervalle, significativité) pour un décideur est une tâche où un LLM est à l'aise, utile dans un secteur où les décisions sont prises par des non-statisticiens.
- *Productivité* : structuration d'un rapport, génération et relecture de code, traduction entre R et Python.

**Inconvénients et risques.**
- *Hallucination statistique* : un LLM peut produire des p-values, des ordres de modèle ou des causalités plausibles mais non vérifiées ; en énergie, la tentation est grande d'attribuer une baisse de consommation à une cause unique (sobriété, prix, météo) alors que les données ne permettent pas de les séparer (section 7.2).
- *Absence d'accès aux données réelles* : le LLM ne voit que ce qu'on lui transmet ; il ne peut ni vérifier la qualité des données, ni détecter une rupture non décrite, et ses connaissances sur des événements récents (crise de 2022, hivers suivants) peuvent être incomplètes.
- *Simplification excessive* : une vulgarisation fidèle à la moyenne peut masquer l'incertitude (intervalles, un seul hiver de test) et pousser à une surconfiance.
- *Reproductibilité et traçabilité* : une même requête peut donner des réponses différentes ; pour un usage opérationnel (réseau électrique), les décisions doivent reposer sur des résultats calculés et auditables, pas sur un texte généré.
- *Confidentialité et coût* : des données d'exploitation sensibles ne doivent pas être transmises à un service externe sans précaution.

**Notre position.** Le LLM est un outil de cadrage et de communication ; il ne remplace ni les calculs, ni les diagnostics, ni la vérification de chaque affirmation contre les fichiers de résultats (section 5.6).
