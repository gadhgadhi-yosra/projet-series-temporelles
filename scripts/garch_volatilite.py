"""Volatilité conditionnelle de l'AR-GARCH(1,2)-t et lien avec des événements connus (section 3.3).

Reprend à l'identique la spécification du notebook 05 (régression de calendrier, AR creux [1,2,7,8,14],
GARCH(1,2) à loi de Student, apprentissage uniquement), car le notebook ne sauvegarde pas la série σ_t.
Sorties : exports/garch_volatilite_conditionnelle.csv, exports/garch_volatilite_evenements.csv,
          figures/ghada/garch_volatilite_evenements.png
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from arch import arch_model

ROOT = Path(__file__).resolve().parent.parent
SC = 100.0                      # unité de 100 GWh : stabilité numérique de l'optimiseur (comme le notebook 05)
AR_LAGS = [1, 2, 7, 8, 14]      # AR creux retenu par BIC dans le notebook 05

df = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date']).set_index('date').asfreq('D')
n_train = int(len(df) * 0.9)
dev = df.iloc[:n_train]
T0 = pd.Timestamp('2016-01-01')


def build_exog(idx, k_fourier=3):
    """Calendrier : Fourier annuel, jours de la semaine, jour férié (même définition que le notebook 05)."""
    d = (idx - T0).days.to_numpy()
    X = pd.DataFrame(index=idx)
    for k in range(1, k_fourier + 1):
        X[f'sin{k}'] = np.sin(2 * np.pi * k * d / 365.25)
        X[f'cos{k}'] = np.cos(2 * np.pi * k * d / 365.25)
    for j in range(1, 7):
        X[f'dow{j}'] = (idx.dayofweek == j).astype(float)
    X['ferie'] = df['ferie'].reindex(idx).fillna(0).to_numpy()
    return X


X = build_exog(df.index)
seas_fit = sm.OLS(dev['conso_gwh'], sm.add_constant(X.loc[dev.index])).fit()
ecarts = dev['conso_gwh'] - pd.Series(seas_fit.predict(sm.add_constant(X.loc[dev.index])), index=dev.index)
res = arch_model(ecarts / SC, mean='AR', lags=AR_LAGS, rescale=False, vol='GARCH', p=1, q=2, dist='t').fit(
    disp='off', options={'maxiter': 500})
print(f'R² calendrier = {seas_fit.rsquared:.3f} ; log-vraisemblance = {res.loglikelihood:.1f} ; BIC = {res.bic:.0f} ; '
      f'α1 = {res.params["alpha[1]"]:.3f} ; ν = {res.params["nu"]:.2f}')

sigma = (res.conditional_volatility * SC).rename('sigma_conditionnel_gwh')
out = pd.DataFrame({'ecart_saisonnalite_gwh': ecarts, 'sigma_conditionnel_gwh': sigma})
out.index.name = 'date'
out.to_csv(ROOT / 'exports' / 'garch_volatilite_conditionnelle.csv')

# Événements cités dans les notebooks 02 et 03 du projet (dates des vagues de froid, confinement, crise énergétique).
EVENEMENTS = [
    ('Vague de froid de janvier 2017', '2017-01-01', '2017-01-31'),
    ('Vague de froid « Moscou-Paris » (fin février 2018)', '2018-02-20', '2018-03-05'),
    ('Premier confinement', '2020-03-17', '2020-05-10'),
    ('Vague de froid de janvier 2021', '2021-01-01', '2021-01-31'),
    ('Hiver 2022-23 (sobriété, décembre 2022 et janvier 2023)', '2022-12-01', '2023-01-31'),
]
rows = []
base = sigma.median()
for nom, debut, fin in EVENEMENTS:
    w = sigma.loc[debut:fin]
    rows.append({'événement': nom, 'début': debut, 'fin': fin, 'sigma moyen (GWh/jour)': w.mean(),
                 'sigma maximal (GWh/jour)': w.max(), 'date du maximum': w.idxmax().date(),
                 'sigma médian de toute la période (GWh/jour)': base, 'rapport maximum / médiane': w.max() / base})
pd.DataFrame(rows).to_csv(ROOT / 'exports' / 'garch_volatilite_evenements.csv', index=False)

# Dix plus fortes valeurs de σ_t, espacées d'au moins 30 jours (un pic = un épisode).
top, taken = [], []
for date, val in sigma.sort_values(ascending=False).items():
    if all(abs((date - d).days) > 30 for d in taken):
        taken.append(date)
        top.append((date.date(), val))
    if len(top) == 10:
        break
pd.DataFrame(top, columns=['date', 'sigma_conditionnel_gwh']).to_csv(ROOT / 'exports' / 'garch_pics_volatilite.csv', index=False)

fig, ax = plt.subplots(figsize=(11, 3.6))
ax.plot(sigma.index, sigma, lw=0.8, color='#c0392b')
for nom, debut, fin in EVENEMENTS:
    ax.axvspan(pd.Timestamp(debut), pd.Timestamp(fin), color='#2a78d6', alpha=0.25)
ax.set_ylabel('σ conditionnel (GWh/jour)')
ax.set_title("Volatilité conditionnelle de l'AR-GARCH(1,2)-t et événements (bandes bleues)")
fig.tight_layout()
fig.savefig(ROOT / 'figures' / 'ghada' / 'garch_volatilite_evenements.png', dpi=150)
pd.set_option('display.width', 250)
print(pd.DataFrame(rows).round(2).to_string())
print(pd.DataFrame(top, columns=['date', 'sigma']).round(1).to_string())
