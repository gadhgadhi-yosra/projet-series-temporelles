**Recommandations de gestion, par ordre de priorité**

**1. Utiliser AR-GARCH(1,2)-t comme prévision de référence et raisonner sur son intervalle, pas sur la seule valeur centrale.**
- *Chiffres.* RMSE de test de 74,45 GWh/jour, la plus faible du tableau, et couverture de 95,9 % pour un intervalle annoncé à 95 %. C'est le seul modèle dont l'intervalle est fourni ici.
- *Limites et risques.* Le témoin à variance constante fait aussi bien en précision (74,06) : le choix d'AR-GARCH se justifie par ses intervalles, pas par sa valeur centrale. La couverture de 95,9 % est une moyenne sur 390 jours ; rien n'indique qu'elle vaut pour chaque saison ni pour chaque horizon.

**2. Dimensionner la marge de sécurité sur la borne haute de l'intervalle, et la réviser chaque jour.**
- *Chiffres.* La borne haute est de 1 128,01 GWh le mardi 1er septembre et de 1 186,42 GWh le lundi 7 septembre. La largeur de l'intervalle passe d'environ 98 GWh le premier jour à environ 273 GWh le septième (différences que je calcule). L'erreur de test croît avec l'horizon : 37,9 GWh à un jour, 96,2 GWh à sept jours.
- *Recommandation.* Prévoir une marge plus large pour la fin de semaine que pour le lendemain, et refaire la prévision chaque jour plutôt que de s'appuyer sur celle faite sept jours plus tôt.
- *Limites et risques.* Un intervalle à 95 % laisse, par construction, environ un jour sur vingt en dehors. Les erreurs les plus fortes peuvent se concentrer sur certains épisodes (les données ne disent pas lesquels). L'intervalle ne tient pas compte de l'incertitude sur les paramètres du modèle.

**3. Anticiper le niveau le plus élevé de la semaine en milieu de semaine, et le creux le dimanche.**
- *Chiffres.* Les prévisions les plus hautes concernent le mercredi 2 septembre (de 1 082,29 à 1 110,17 GWh selon les modèles) et le jeudi 3 septembre (de 1 082,22 à 1 108,48 GWh). Le creux est le dimanche 6 septembre (de 906,98 à 938,23 GWh).
- *Recommandation.* Planifier de préférence les opérations qui réduisent la capacité disponible (maintenance) le dimanche, et éviter le milieu de semaine.
- *Limites et risques.* Il s'agit d'un profil hebdomadaire ordinaire, pas d'un « pic » exceptionnel : aucune valeur prévue n'approche les niveaux qu'une vague de froid pourrait produire, et ces données ne permettent pas d'en anticiper une. Le creux du week-end est vraisemblablement lié à la baisse d'activité, mais cette cause n'est pas démontrée par les données fournies.

**4. Surveiller les jours où les modèles divergent.**
- *Chiffres.* Le lundi 7 septembre, les prévisions vont de 1 044,81 GWh (SARIMA + LSTM) à 1 078,25 GWh (LSTM), soit un écart d'environ 33 GWh (différence que je calcule), le plus grand de la semaine.
- *Recommandation.* Traiter cet écart comme un signal d'incertitude supplémentaire et suivre ce jour de plus près.
- *Limites et risques.* Des modèles d'accord entre eux peuvent se tromper ensemble : ils utilisent les mêmes données et aucun n'a de prévision météo. L'accord entre modèles n'est pas une mesure de fiabilité.

**5. Ne pas utiliser Prophet ni les méthodes naïves pour la prévision à sept jours.**
- *Chiffres.* RMSE de 101,79 GWh/jour pour Prophet, 109,13 pour la persistance et 113,93 pour le naïf saisonnier, contre 74,45 pour AR-GARCH ; la couverture de Prophet n'est que de 88,5 %.
- *Limites et risques.* Ce classement vaut pour ce test ; Prophet est par ailleurs réajusté chaque semaine, ce qui n'est pas le cas des autres modèles. Les méthodes naïves restent utiles comme garde-fou : une prévision qui s'en écarte beaucoup mérite d'être vérifiée.

**6. Garder un second modèle en parallèle.**
- *Chiffres.* Le LSTM (75,07) et le GRU (76,40) ont des erreurs très proches de celle d'AR-GARCH.
- *Limites et risques.* Ils ne fournissent pas d'intervalle et comptent 4 900 et 3 684 paramètres : ils sont plus difficiles à expliquer et à auditer.

**Ce que ces données ne permettent pas de décider**

- Le niveau de marge acceptable : il dépend de la capacité disponible et du coût d'une défaillance, absents des données.
- Le comportement en cas d'événement exceptionnel (vague de froid ou de chaleur, incident sur le réseau) : aucun modèle n'utilise la météo.
- La fiabilité des prévisions pour cette semaine précise : les valeurs réelles de septembre 2026 ne sont pas fournies.
- La stabilité du classement des modèles : il repose sur une seule période de test de 390 jours.
- Toute décision d'exploitation réelle : ces prévisions sont un exercice de modélisation, pas un outil validé pour la conduite du réseau.
