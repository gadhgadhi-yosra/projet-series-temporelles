"""Validation croisée temporelle d'AR-GARCH(1,2)-t et du témoin AR à variance constante (section 6.6, annexe A).

Mêmes plis et même protocole que scripts/cv_temporelle.py : chaque pli apprend sur [début de la série, date d'origine],
puis prévoit les 56 jours suivants par blocs de 7 jours, à paramètres fixes. Les fonctions de prévision sont celles du
notebook 05 (régression de calendrier, AR creux, GARCH, quantile de Student), relues dans le notebook pour ne pas les
recopier : la régression de calendrier et le modèle sont ré-estimés dans chaque pli, sur sa seule période d'apprentissage.
La spécification (retards 1, 2, 7, 8 et 14, GARCH(1,2), loi de Student) est celle retenue dans le notebook 05 sur tout
l'apprentissage ; elle n'est pas re-sélectionnée dans chaque pli, comme pour le SARIMA et les réseaux de cv_temporelle.py.
Tous les plis se situent dans l'apprentissage (jusqu'au 6 août 2025) : le test externe ne sert qu'au contrôle de cohérence.

Sorties : exports/cv_ar_garch.csv (détail par pli), exports/cv_ar_garch_resume.csv (résumé, avec les modèles de
          exports/lstm_gru/cv_temporelle.csv pour comparaison)
"""
import ast
import json
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from arch import arch_model
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')

HORIZON, ALPHA, SC = 7, 0.05, 100.0   # blocs de 7 jours, intervalles à 95 %, unité de 100 GWh (comme le notebook 05)
AR_LAGS = [1, 2, 7, 8, 14]            # AR creux retenu par BIC dans le notebook 05
TEST_DAYS = 56                        # 8 blocs de 7 jours, comme scripts/cv_temporelle.py
COLS = ['origine', 'date', 'horizon', 'observe', 'prevision', 'borne_inferieure_95', 'borne_superieure_95']
SPECS = {'AR-GARCH(1,2)-t': dict(vol='GARCH', p=1, q=2, dist='t'),
         'Témoin AR à variance constante': dict(vol='Constant', dist='normal')}
# Mêmes plis que scripts/cv_temporelle.py : (date de fin d'apprentissage, saison du test).
PLIS = [('2021-12-19', 'hiver'), ('2022-12-18', 'hiver'), ('2023-06-11', 'été'), ('2024-12-15', 'hiver'),
        ('2025-06-11', 'été')]

df = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date']).set_index('date').asfreq('D')
N_APPRENTISSAGE = int(len(df) * 0.9)  # 3 506 jours

# Définitions du notebook 05 (calendrier, ajustement, quantile, prévision glissante par blocs).
NAMES = {'build_exog', 'to_frame', 'forecast_metrics', 'fit_arch', 'arch_quantile', 'wf_arch'}
notebook = json.loads((ROOT / '05_var_vecm_garch_prophet.ipynb').read_text(encoding='utf-8'))
nodes = [node for cell in notebook['cells'] if cell['cell_type'] == 'code'
         for node in ast.parse(''.join(cell['source'])).body
         if isinstance(node, ast.FunctionDef) and node.name in NAMES]
assert {n.name for n in nodes} == NAMES
ns = dict(np=np, pd=pd, stats=stats, arch_model=arch_model, df=df, T0=pd.Timestamp('2016-01-01'), FERIE=df['ferie'],
          HORIZON=HORIZON, ALPHA=ALPHA, SC=SC, AR_LAGS=AR_LAGS, COLS=COLS)
exec(compile(ast.Module(body=nodes, type_ignores=[]), '05_var_vecm_garch_prophet.ipynb', 'exec'), ns)
X_all = ns['build_exog'](df.index)


def prevoir(end, stop):
    """Ajuste les deux modèles sur les `end` premiers jours, puis prévoit [end, stop) par blocs de 7 jours."""
    train = df.index[:end]
    seas_fit = sm.OLS(df['conso_gwh'].loc[train], sm.add_constant(X_all.loc[train])).fit()
    seas_all = pd.Series(seas_fit.predict(sm.add_constant(X_all, has_constant='add')), index=df.index)
    ecarts = (df['conso_gwh'] - seas_all).iloc[:stop]   # rien au-delà de la fin du pli n'est transmis au modèle
    ns.update(seas_all=seas_all, dev_all=ecarts)
    sorties = {}
    for nom, spec in SPECS.items():
        t0 = time.perf_counter()
        _, res = ns['fit_arch'](ecarts.iloc[:end], spec)
        pred = ns['wf_arch'](res, spec, end, stop)
        sorties[nom] = (pred, res.convergence_flag == 0, time.perf_counter() - t0)
    return sorties


# Contrôle de cohérence : sur le découpage du rapport (apprentissage puis test externe), le script doit redonner
# les prévisions du notebook 05 ; sinon le protocole ne serait pas le même et la validation croisée ne vaudrait rien.
reference = pd.read_csv(ROOT / 'exports' / 'ghada' / 'predictions_test_detail.csv', parse_dates=['date'])
reference = reference[reference['modele'] == 'garch'].set_index('date')['prevision']
controle = prevoir(N_APPRENTISSAGE, len(df))
ecart_max = float(np.abs(controle['AR-GARCH(1,2)-t'][0].set_index('date')['prevision'] - reference).max())
assert ecart_max < 1e-3, f'prévisions du test non reproduites (écart maximal {ecart_max:.4f} GWh/jour)'
for nom, (pred, _, _) in controle.items():
    m = ns['forecast_metrics'](pred)
    print(f"Contrôle sur le test externe — {nom} : RMSE {m['RMSE']:.2f}, couverture {100 * m['couverture_95']:.1f} %")
print(f'Écart maximal avec les prévisions exportées par le notebook 05 : {ecart_max:.2e} GWh/jour')

rows = []
for numero, (fin, saison) in enumerate(PLIS, start=1):
    end = df.index.get_loc(pd.Timestamp(fin)) + 1
    stop = end + TEST_DAYS
    assert stop <= N_APPRENTISSAGE, 'un pli déborde sur le test externe'
    info = {'pli': numero, 'saison du test': saison, 'fin apprentissage': df.index[end - 1].date(),
            'début test': df.index[end].date(), 'fin test': df.index[stop - 1].date(), 'jours apprentissage': end}
    for nom, (pred, converge, duree) in prevoir(end, stop).items():
        assert len(pred) == TEST_DAYS and (pred['date'] > pred['origine']).all()
        m = ns['forecast_metrics'](pred)
        rows.append({**info, 'modèle': nom, 'RMSE': m['RMSE'], 'MAE': m['MAE'], 'MAPE (%)': m['MAPE (%)'],
                     'couverture à 95 % (%)': 100 * m['couverture_95'], 'largeur moyenne à 95 % (GWh/jour)': m['largeur_moy_95'],
                     'temps de calcul du pli (s)': duree, 'convergence': 'oui' if converge else 'non'})
    print(f'Pli {numero} ({saison}) : ' + ', '.join(f"{r['modèle']} {r['RMSE']:.1f}" for r in rows[-2:]), flush=True)

detail = pd.DataFrame(rows)
detail.to_csv(ROOT / 'exports' / 'cv_ar_garch.csv', index=False)

# Résumé commun avec les modèles déjà validés sur les mêmes plis (LSTM, GRU, SARIMA, naïf saisonnier).
autres = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'cv_temporelle.csv')
assert autres.groupby('pli')['fin apprentissage'].first().astype(str).tolist() == [fin for fin, _ in PLIS]
tous = pd.concat([detail, autres], ignore_index=True)
resume = tous.groupby('modèle')[['RMSE', 'MAE', 'MAPE (%)']].mean().add_suffix(' (moyenne des 5 plis)')
resume['RMSE moyenne des plis d\'hiver'] = tous[tous['saison du test'] == 'hiver'].groupby('modèle')['RMSE'].mean()
resume['RMSE moyenne des plis d\'été'] = tous[tous['saison du test'] == 'été'].groupby('modèle')['RMSE'].mean()
resume['rang moyen (1 = meilleur)'] = tous.assign(rang=tous.groupby('pli')['RMSE'].rank()).groupby('modèle')['rang'].mean()
resume['plis où le modèle a la plus petite RMSE'] = (tous.loc[tous.groupby('pli')['RMSE'].idxmin(), 'modèle']
                                                    .value_counts().reindex(resume.index).fillna(0).astype(int))
couverture = detail.groupby('modèle')['couverture à 95 % (%)']
resume['couverture moyenne à 95 % (%)'] = couverture.mean()
resume['couverture moyenne des plis d\'hiver (%)'] = detail[detail['saison du test'] == 'hiver'].groupby('modèle')['couverture à 95 % (%)'].mean()
resume = resume.sort_values('RMSE (moyenne des 5 plis)')
resume.to_csv(ROOT / 'exports' / 'cv_ar_garch_resume.csv')

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
print(tous.pivot(index='modèle', columns='pli', values='RMSE').round(2).to_string())
print(detail.pivot(index='modèle', columns='pli', values='couverture à 95 % (%)').round(1).to_string())
print(resume.round(2).to_string())
