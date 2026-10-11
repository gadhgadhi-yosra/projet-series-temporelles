## 3.4 Réplication en R et comparaison avec Python

Le sujet demande le socle classique en R **et** en Python. Nous avons donc refait en R (version 4.5.2, notebook `06_section3_R.ipynb`) la stationnarité, le SARIMA (`forecast`, `tseries`, `urca`), le VAR, le test de Johansen et le VECM (`vars`, `urca`) et l'AR-GARCH (`rugarch`), avec les mêmes données, le même découpage (3 506 jours d'apprentissage, 390 jours de test), la même validation interne et la même graine (42), pour vérifier que les conclusions ne dépendent pas du logiciel. Le modèle Prophet n'est pas répliqué en R.

[[TAB:r_python|Comparaison des résultats R et Python (extrait)|Les deux implémentations coïncident à la troisième décimale ; seuls les paramètres du GARCH s'écartent légèrement, à cause d'optimiseurs différents.]]

| Élément | Python | R |
|---|---|---|
| ADF de la consommation brute | −4,10 | −4,10 |
| KPSS de la consommation brute | 0,40 | 0,40 |
| SARIMA retenu : RMSE de test (GWh/jour) | 82,38 | 82,38 |
| Ordre du VAR retenu (BIC) | 3 | 3 |
| Granger température → consommation (F) | 118,57 | 118,57 |
| Johansen, statistique de la trace pour r = 0 | 337,72 | 337,72 |
| VECM : demi-vie de correction (jours) | 37,90 | 37,92 |
| AR-GARCH(1,2)-t : RMSE de test (GWh/jour) | 74,45 | 74,44 |
| AR-GARCH : couverture à 95 % | 95,9 % | 95,6 % |

**25 éléments sur 27 sont identiques à 0,1 % près** (annexe A, tableau @tab:annexe_r). Les deux seuls écarts supérieurs à 0,1 % concernent le GARCH (paramètre α₁ : 0,35 % ; couverture : 0,27 %, soit un jour sur 390), dus aux optimiseurs de `rugarch` et d'`arch`. Les conclusions sont toutes identiques : le résultat ne dépend pas du logiciel.

**Différences de méthode.** `auto.arima` retient SARIMA(1,0,1)(1,1,0)[7] tandis que `pmdarima` retient SARIMA(2,1,1)(1,0,0)[7] : les recherches pas à pas n'explorent pas l'espace dans le même ordre, et aucune ne bat le modèle identifié par l'ACF/PACF (RMSE de validation de 49,77 et de 48,11 GWh/jour contre 42,68). Les statistiques de Johansen sont identiques, mais les valeurs critiques diffèrent (8,18 en R, 3,84 en Python pour r ≤ 1) car les tables ne sont pas les mêmes ; la conclusion (rang plein) est inchangée.

**Pièges de convention rencontrés.** Avant de comparer deux logiciels, il faut aligner : (1) la procédure ADF (pour la température : −3,37 avec `urca::ur.df` contre −3,48 avec la procédure de `statsmodels`, que la version finale reproduit) ; (2) les tables de valeurs critiques de Johansen ; (3) la correspondance entre le nombre de retards en différences et l'ordre du VAR en niveaux ; (4) l'ordre des paramètres (ARCH, GARCH).

**La réplication comme relecture.** Elle a révélé une erreur d'affichage dans le notebook Python du VAR : une valeur d'environ 0,25 présentée comme « module max des racines » était en réalité le module minimal des valeurs propres ; le module maximal vaut 0,87 (le VAR est stable, la conclusion n'était pas affectée). L'affichage a été corrigé dans le notebook ; la valeur de 0,87 est celle de la sortie R, retrouvée à l'identique (0,8656) en réexécutant la cellule en Python. Elle a aussi révélé que le solveur par défaut de `rugarch` n'est pas reproductible.

**Limite.** R et Python utilisent les mêmes données et le même protocole : cette comparaison valide les implémentations, non le choix des modèles ni leur robustesse sur une autre période.
