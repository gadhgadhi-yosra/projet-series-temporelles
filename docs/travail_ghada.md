# Travail de Ghada — état au 9 octobre 2026

**Notebook** : `05_var_vecm_garch_prophet.ipynb` (à lancer depuis la racine du dépôt). Il utilise `data/daily.csv` de Fayfa sans le modifier.

| Tâche du plan | Où | État |
|---|---|---|
| VAR (ordre AIC/BIC) + Granger | notebook étapes 3 à 9 ; `rapport/section_3_2_var_granger.md` | fait |
| Johansen + VECM (vitesse de correction) | étapes 10–11 ; `rapport/section_3_3_vecm.md` | fait (rang plein : VECM imposé à r = 1, signalé) |
| GARCH(1,1) vs ordre supérieur, résidus standardisés | étape 12 ; `rapport/section_4_3_garch_prophet.md` | fait |
| Prophet | étape 13 ; même section | fait |
| Discussion critique | `rapport/discussion_critique.md` | brouillon, à compléter avec 3.1, 4.1, 4.2, 6 |
| Mise en page et assemblage du rapport | — | à faire dimanche, quand les autres sections sont livrées |

## Livrables partagés (règle du groupe)

- `forecasts/var.csv`, `forecasts/vecm.csv`, `forecasts/garch.csv`, `forecasts/prophet.csv` : colonnes `date, prevision, borne_inferieure_95, borne_superieure_95`, 390 lignes (test du 7 août 2025 au 31 août 2026, prévisions à 1–7 jours par blocs de 7 jours).
- `exports/ghada/` : tables (métriques, diagnostics, Granger, Johansen, choix d'ordres…) et prévisions à 7 jours `previsions_7j_<modèle>.csv` (**1er–7 septembre 2026**, pas des dates d'octobre).
- `figures/ghada/` : figures du rapport.

## Relancer

```sh
pip install -r requirements.txt        # arch et prophet ajoutés
jupyter nbconvert --to notebook --execute --inplace 05_var_vecm_garch_prophet.ipynb
```
Durée : environ 3 minutes (Prophet est ré-ajusté 56 fois par évaluation).

## Pour Anas

Les quatre fichiers `forecasts/*.csv` ont exactement les mêmes dates que `exports/predictions_test.csv` de Yosra (390 jours), ce qui permet le tableau de métriques et les tests de Diebold-Mariano.
