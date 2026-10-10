# Vérification de 07_lstm_gru.ipynb — 10 octobre 2026

Le notebook a été exécuté intégralement : **21 cellules de code sans erreur**, en 500 secondes sur CPU. Les sorties sont enregistrées dans le notebook : sept graphiques, les tableaux de validation et de comparaison, les tests et la conclusion.

## Contenu vérifié

- **LSTM et GRU** : 28 jours d'historique, 32 unités, entraînement de cinq réseaux par configuration, sélection des entrées et des époques sur la validation uniquement.
- **SARIMA + LSTM** : le LSTM prévoit les erreurs des prévisions SARIMA et ajoute sa correction à la première prévision. Les trois ajustements SARIMA convergent. Écarts maximaux avec les exports de la section 3.1 : 0,0094 GWh en validation, 0,0192 GWh sur le test et 0,0003 GWh pour la prévision finale.
- **Comparaison** : dix modèles, mêmes 390 dates et mêmes origines et horizons ; MSE, RMSE, MAE et MAPE calculées sur les mêmes observations. Les autres modèles sont relus dans les exports du groupe ; leurs notebooks n'ont pas été réentraînés pendant cette vérification.
- **Diebold–Mariano** : 45 paires, perte quadratique et perte absolue. Les pertes sont moyennées par bloc complet de sept horizons. Les tests utilisent 55 blocs, soit 385 jours, avec variance HAC Bartlett ; les cinq derniers jours restent inclus dans les métriques descriptives. Correction de Holm sur les 45 paires et sensibilité à la bande HAC.
- **Conclusion** : calculée à partir des résultats, affichée dans le notebook et exportée dans `exports/lstm_gru/conclusion.md`.

## Résultats observés

| Modèle | MSE | RMSE | MAE | MAPE (%) |
|---|---:|---:|---:|---:|
| AR-GARCH(1,2)-t | 5 543,30 | 74,45 | 48,61 | 3,78 |
| LSTM | 5 634,84 | 75,07 | 50,26 | 3,96 |
| GRU | 5 836,62 | 76,40 | 52,40 | 4,16 |
| SARIMA + LSTM | 6 387,63 | 79,92 | 53,84 | 4,27 |
| SARIMA | 6 786,82 | 82,38 | 53,12 | 4,13 |

AR-GARCH obtient les meilleurs scores descriptifs. Sa différence avec LSTM n'est pas significative (p brute 0,913 ; p Holm 1). L'hybride réduit la RMSE du SARIMA de 3 %, mais la différence reste non significative (p brute 0,595 ; p Holm 1). Il ne réduit pas sa MAE ni sa MAPE. La conclusion distingue donc classement observé et supériorité statistique.

## Vérifications automatiques et reproduction

`python -m unittest discover -s tests -v` : **21 tests réussis**, dont 18 consacrés à ce notebook. Les tests vérifient les architectures, les fenêtres d'apprentissage, l'absence de fuite des observations du bloc courant, la récursion, le calendrier, la normalisation, les métriques, DM par une référence indépendante `statsmodels.cov_hac`, et Holm par `statsmodels.multipletests`.

Depuis la racine du projet, sous Windows :

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-lstm-gru.txt
.\.venv\Scripts\python.exe scripts/executer_lstm_gru.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Le script utilise le même interpréteur pour lancer le noyau Jupyter et sauvegarde les sorties après chaque cellule. Le notebook reste aussi exécutable directement avec « Run All » dans un noyau disposant des dépendances.

L'exécution enregistrée utilise Python 3.10.8 et PyTorch 2.12.0 ; les versions complètes et l'empreinte des données sont dans `exports/lstm_gru/verification.json`. L'environnement `.venv` Python 3.11 est également opérationnel et ses dépendances sont cohérentes (`pip check`). pandas 2.3.3 y remplace la version 3.0.6 dont une DLL était bloquée par Windows ; `requirements-lstm-gru.txt` impose pandas < 3. Des versions différentes peuvent produire de légères différences numériques au réentraînement.

Les limites scientifiques restent explicites : validation estivale courte, un seul hiver de test, absence de météo future, erreurs d'apprentissage SARIMA pseudo hors échantillon, et réestimations hebdomadaires de Prophet. Les tests asymptotiques sur 55 origines ne garantissent pas que le classement se reproduise sur une autre période.
