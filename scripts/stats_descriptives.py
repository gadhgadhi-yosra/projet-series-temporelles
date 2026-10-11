"""Statistiques descriptives de la série (entrée de la section 5 du rapport).

Calculées sur l'apprentissage uniquement (3 506 premiers jours), comme l'analyse exploratoire.
Sortie : exports/stats_descriptives.csv
"""
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, kpss

ROOT = Path(__file__).resolve().parent.parent
data = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date']).set_index('date').asfreq('D')
n_train = int(len(data) * 0.9)  # découpage chronologique 90 % / 10 %, identique pour tout le projet
train = data.iloc[:n_train]

rows = []
for name, label, unit in [('conso_gwh', 'Consommation électrique', 'GWh/jour'), ('temp_moy', 'Température moyenne nationale', '°C')]:
    s = train[name].astype(float)
    row = {'série': label, 'unité': unit, 'observations': len(s), 'début': s.index[0].date(), 'fin': s.index[-1].date(),
           'moyenne': s.mean(), 'variance': s.var(ddof=1), 'écart-type': s.std(ddof=1),
           'minimum': s.min(), 'maximum': s.max(),
           'asymétrie (skewness)': stats.skew(s, bias=False),
           'aplatissement excédentaire (kurtosis)': stats.kurtosis(s, fisher=True, bias=False)}
    # Mêmes réglages que le notebook 02 : ADF avec retards choisis par AIC, KPSS autour d'une constante.
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        adf_stat, adf_p, *_ = adfuller(s, autolag='AIC')
        kpss_stat, kpss_p, *_ = kpss(s, regression='c', nlags='auto')
    row.update({'ADF statistique': adf_stat, 'ADF p-value': adf_p, 'KPSS statistique': kpss_stat, 'KPSS p-value': kpss_p})
    if name == 'conso_gwh':
        # Différences simples et saisonnière (7 jours) : ordres de différenciation étudiés en section 2.
        for suffix, serie in [('différence simple', s.diff().dropna()), ('différence simple et saisonnière', s.diff().diff(7).dropna())]:
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                a, ap, *_ = adfuller(serie, autolag='AIC')
                k, kp, *_ = kpss(serie, regression='c', nlags='auto')
            rows.append({'série': f'Consommation électrique ({suffix})', 'unité': unit, 'observations': len(serie),
                         'début': serie.index[0].date(), 'fin': serie.index[-1].date(),
                         'moyenne': serie.mean(), 'variance': serie.var(ddof=1), 'écart-type': serie.std(ddof=1),
                         'minimum': serie.min(), 'maximum': serie.max(),
                         'asymétrie (skewness)': stats.skew(serie, bias=False),
                         'aplatissement excédentaire (kurtosis)': stats.kurtosis(serie, fisher=True, bias=False),
                         'ADF statistique': a, 'ADF p-value': ap, 'KPSS statistique': k, 'KPSS p-value': kp})
    rows.insert(len(rows) - (2 if name == 'conso_gwh' else 0), row)

out = pd.DataFrame(rows)
out.to_csv(ROOT / 'exports' / 'stats_descriptives.csv', index=False)
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
print(out.round(4).T.to_string())
