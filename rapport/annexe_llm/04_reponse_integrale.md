**Ce que disent les résultats, en clair**

**1. Le modèle le plus précis.** Sur les 390 jours de test, le modèle appelé AR-GARCH(1,2)-t a la plus petite erreur : 74,45 GWh par jour (RMSE). Pour une consommation journalière moyenne de 1 258,93 GWh, cela représente environ 6 % (rapport que je calcule). Autrement dit, quand ce modèle annonce une consommation, il faut s'attendre à un écart de cet ordre, plus petit la plupart des jours et nettement plus grand certains jours : la RMSE pèse davantage les grosses erreurs. Son erreur « typique » (MAE) est de 48,61 GWh, soit 3,78 % en moyenne (MAPE).

**2. Plus petite erreur ne veut pas dire supériorité démontrée.** Deux modèles peuvent avoir des erreurs différentes sur une année simplement par hasard. Le test de Diebold–Mariano mesure si l'écart est trop grand pour être dû au hasard. Après correction pour le grand nombre de comparaisons, AR-GARCH n'est distingué ni du LSTM (p corrigée 1,000), ni du GRU (1,000), ni du VAR(3) (1,000), ni de l'hybride SARIMA + LSTM (1,000), ni du SARIMA (0,890), ni du VECM (0,890). Il n'est clairement meilleur que Prophet (0,029) et que la persistance (0,000). Contre le naïf saisonnier, le verdict dépend de la façon de mesurer l'erreur : 0,157 avec la perte quadratique, 0,0005 avec la perte absolue.

**3. Comparaison des modèles**

- *Précision.* Cinq modèles se tiennent entre 74,45 et 79,92 GWh : AR-GARCH, LSTM (75,07), GRU (76,40), VAR(3) (78,96) et l'hybride (79,92). Le SARIMA suit (82,38). Prophet (101,79) et les deux méthodes naïves (109,13 et 113,93) sont nettement derrière.
- *Qualité des intervalles.* Un intervalle annoncé à 95 % devrait contenir la vraie valeur 95 fois sur 100. AR-GARCH y parvient (95,9 %), le SARIMA presque (94,4 %), le VAR un peu moins (93,1 %), le VECM moins encore (91,3 %) ; ceux de Prophet sont trop étroits (88,5 %). Le LSTM, le GRU et l'hybride ne fournissent pas d'intervalle.
- *Lisibilité.* Les chiffres fournis ne mesurent pas la lisibilité. On peut seulement noter le nombre de paramètres : 5 pour le SARIMA, 25 pour AR-GARCH, 40 pour le VAR, contre 4 900 pour le LSTM et 3 684 pour le GRU. Un modèle à quelques paramètres est en général plus facile à expliquer.
- *Coût de calcul.* Un ajustement prend 0,10 seconde pour AR-GARCH, 2,08 secondes pour le SARIMA, 7,73 secondes pour le LSTM et 15,18 secondes pour le GRU. Tous ces temps sont faibles ; Prophet (1,78 seconde) est réajusté chaque semaine, ce qui multiplie son coût.

**4. Ce qu'on peut conclure, et ce qu'on ne peut pas**

- On peut dire que les modèles qui tiennent compte du passé récent font nettement mieux que la simple répétition de la dernière valeur.
- On peut dire qu'AR-GARCH est le meilleur observé et qu'il donne les intervalles les mieux calibrés.
- On ne peut pas dire qu'il sera encore le meilleur l'an prochain : le test porte sur une seule période de 390 jours, et l'écart avec ses concurrents directs n'est pas démontré.
- Le « témoin » sans modélisation de la variance fait aussi bien en précision (74,06) : la partie GARCH n'apporte donc pas de précision, mais elle améliore la couverture des intervalles (95,9 % contre 93,3 %).
- Aucun modèle n'utilise de prévision météo ; les données ne disent pas ce que cette information apporterait.
- Les chiffres ne disent rien du coût d'une erreur pour l'exploitant, qui devrait guider le choix final.
