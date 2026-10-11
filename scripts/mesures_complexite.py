"""Mesure du nombre de paramètres estimés et du temps d'un ajustement pour chaque modèle (section 6).

Chaque modèle est ajusté une fois sur l'apprentissage complet (3 506 jours), avec la spécification retenue dans
les notebooks. Les temps sont des temps d'horloge sur la machine d'exécution (un seul fil de calcul pour les
réseaux) : ils servent à comparer les coûts relatifs, pas à donner des valeurs absolues.
Sortie : exports/complexite_modeles.csv
"""
import ast
import json
import platform
import time
import warnings
from copy import deepcopy
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import torch
from arch import arch_model
from prophet import Prophet
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.vector_ar.var_model import VAR
from statsmodels.tsa.vector_ar.vecm import VECM
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

ROOT = Path(__file__).resolve().parent.parent
warnings.filterwarnings('ignore')
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)
WINDOW, BLOCK, HIDDEN, BATCH, LEARNING_RATE, MAX_EPOCHS, PATIENCE = 28, 7, 32, 64, 1e-3, 40, 7

data = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date']).set_index('date').asfreq('D')
n_train = int(len(data) * 0.9)
dev = data.iloc[:n_train]
config = json.loads((ROOT / 'exports' / 'lstm_gru' / 'configuration.json').read_text(encoding='utf-8'))
selection = json.loads((ROOT / 'exports' / 'selection_avant_test.json').read_text(encoding='utf-8'))
rows = []


def chrono(fonction):
    t0 = time.perf_counter()
    objet = fonction()
    return objet, time.perf_counter() - t0


# --- SARIMA(2,1,1)(0,1,1)[7]
spec = dict(order=tuple(selection['order']), seasonal_order=tuple(selection['seasonal_order']), trend=selection['trend'],
            enforce_stationarity=True, enforce_invertibility=True)
sarima, t_sarima = chrono(lambda: SARIMAX(dev['conso_gwh'], **spec).fit(disp=False, maxiter=500))
n_sarima = len(sarima.params)
rows.append(('SARIMA(2,1,1)(0,1,1)[7]', n_sarima, t_sarima, 1, 'paramètres : 2 AR, 1 MA, 1 MA saisonnier et variance du bruit'))

# --- Calendrier commun au VAR, au VECM et à l'AR-GARCH (définition du notebook 05)
T0 = pd.Timestamp('2016-01-01')


def build_exog(idx, k_fourier=3):
    d = (idx - T0).days.to_numpy()
    X = pd.DataFrame(index=idx)
    for k in range(1, k_fourier + 1):
        X[f'sin{k}'] = np.sin(2 * np.pi * k * d / 365.25)
        X[f'cos{k}'] = np.cos(2 * np.pi * k * d / 365.25)
    for j in range(1, 7):
        X[f'dow{j}'] = (idx.dayofweek == j).astype(float)
    X['ferie'] = data['ferie'].reindex(idx).fillna(0).to_numpy()
    return X


X = build_exog(data.index)
ENDOG = ['conso_gwh', 'temp_moy']

# --- VAR(3) avec calendrier exogène
var_res, t_var = chrono(lambda: VAR(dev[ENDOG], exog=X.loc[dev.index]).fit(3))
rows.append(('VAR(3)', int(var_res.params.size), t_var, 1, 'coefficients des deux équations (constante, retards, calendrier)'))

# --- VECM(k = 12, r = 1) avec calendrier exogène
vecm_res, t_vecm = chrono(lambda: VECM(dev[ENDOG], exog=X.loc[dev.index], k_ar_diff=12, coint_rank=1, deterministic='co').fit())
n_vecm = int(vecm_res.alpha.size + (vecm_res.beta.size - 1) + vecm_res.gamma.size + vecm_res.det_coef.size)
rows.append(('VECM(12, r = 1)', n_vecm, t_vecm, 1, 'α, β (normalisé), coefficients de court terme, constante et calendrier'))

# --- AR-GARCH(1,2)-t : régression de calendrier puis AR creux et GARCH sur les écarts
def fit_ar_garch():
    ols = sm.OLS(dev['conso_gwh'], sm.add_constant(X.loc[dev.index])).fit()
    ecarts = dev['conso_gwh'] - ols.fittedvalues
    res = arch_model(ecarts / 100.0, mean='AR', lags=[1, 2, 7, 8, 14], rescale=False, vol='GARCH', p=1, q=2, dist='t').fit(
        disp='off', options={'maxiter': 500})
    return ols, res


(ols, garch), t_garch = chrono(fit_ar_garch)
rows.append(('AR-GARCH(1,2)-t', int(len(ols.params) + len(garch.params)), t_garch, 1,
             'régression de calendrier (14) + AR creux (constante, 5 retards) + variance (ω, α, 2 β) + loi de Student (ν)'))

# --- Témoin : même régression de calendrier et même AR creux, mais variance constante (sans GARCH)
def fit_temoin():
    ols_t = sm.OLS(dev['conso_gwh'], sm.add_constant(X.loc[dev.index])).fit()
    ecarts_t = dev['conso_gwh'] - ols_t.fittedvalues
    res_t = arch_model(ecarts_t / 100.0, mean='AR', lags=[1, 2, 7, 8, 14], rescale=False, vol='Constant', dist='normal').fit(
        disp='off', options={'maxiter': 500})
    return ols_t, res_t


(ols_t, temoin), t_temoin = chrono(fit_temoin)
rows.append(('Témoin : AR creux, variance constante', int(len(ols_t.params) + len(temoin.params)), t_temoin, 1,
             'régression de calendrier (14) + AR creux (constante, 5 retards) + variance constante'))

# --- Prophet (tendance flexible additive, jours fériés)
holidays = pd.DataFrame({'holiday': 'ferie', 'ds': data.index[data['ferie'] == 1]})
prophet, t_prophet = chrono(lambda: Prophet(changepoint_prior_scale=0.5, seasonality_mode='additive', interval_width=0.95,
                                            daily_seasonality=False, holidays=holidays).fit(
    pd.DataFrame({'ds': dev.index, 'y': dev['conso_gwh'].to_numpy()})))
# Paramètres du modèle Prophet : tendance (k, m, 25 variations delta), bruit et coefficients de saisonnalités/jours fériés (beta).
n_prophet = int(sum(np.size(prophet.params[k]) for k in ('k', 'm', 'delta', 'sigma_obs', 'beta')))
rows.append(('Prophet', n_prophet, t_prophet, 56,
             'tendance (k, m, 25 variations), bruit et 27 coefficients de saisonnalité et de jours fériés ; ré-ajusté à chaque bloc de 7 jours (56 ajustements pour le test)'))

# --- Réseaux récurrents : définitions reprises du notebook 07
NAMES = {'RecurrentForecaster', 'Standardizer', 'network_inputs', 'training_set', 'forecast_blocks', 'train_network', 'rmse', 'scores'}
notebook = json.loads((ROOT / '07_lstm_gru.ipynb').read_text(encoding='utf-8'))
nodes = [node for cell in notebook['cells'] if cell['cell_type'] == 'code'
         for node in ast.parse(''.join(cell['source'])).body
         if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in NAMES]
ns = dict(np=np, torch=torch, nn=nn, DataLoader=DataLoader, TensorDataset=TensorDataset, deepcopy=deepcopy, WINDOW=WINDOW,
          BLOCK=BLOCK, HIDDEN=HIDDEN, BATCH=BATCH, LEARNING_RATE=LEARNING_RATE, MAX_EPOCHS=MAX_EPOCHS, PATIENCE=PATIENCE)
exec(compile(ast.Module(body=nodes, type_ignores=[]), '07_lstm_gru.ipynb', 'exec'), ns)
weekday = data.index.dayofweek.to_numpy()
calendar = np.column_stack([np.sin(2 * np.pi * weekday / 7), np.cos(2 * np.pi * weekday / 7), data['ferie'].to_numpy(dtype=float)])
y = data['conso_gwh'].to_numpy(dtype=float)
scaler = ns['Standardizer'](y[:n_train])
scaled = scaler.transform(y)
n_net = {}
t_net = {}
for kind in ('LSTM', 'GRU'):
    epochs = config['direct'][kind]['epochs'][0]  # nombre d'époques retenu pour la première graine
    (model, _, _), t_net[kind] = chrono(lambda: ns['train_network'](kind, scaled, calendar, n_train, 42, epochs=epochs))
    n_net[kind] = int(sum(p.numel() for p in model.parameters()))
    rows.append((kind, n_net[kind], t_net[kind], 5,
                 f'un réseau, {epochs} époques ; le modèle évalué moyenne 5 réseaux (5 graines)'))

# --- Hybride SARIMA + LSTM : SARIMA + LSTM des erreurs (un réseau)
epochs_h = config['hybrid']['epochs'][0]
(model_h, _, _), t_h = chrono(lambda: ns['train_network']('LSTM', scaled, calendar, n_train, 42, epochs=epochs_h))
rows.append(('SARIMA + LSTM', n_sarima + n_net['LSTM'], t_sarima + t_h, 6,
             f"SARIMA + un LSTM ({epochs_h} époques) ; temps approché : le LSTM est entraîné ici sur la consommation, "
             "génération des erreurs d'apprentissage non incluse ; le modèle évalué moyenne 5 réseaux"))
rows.append(('Naïf saisonnier', 0, 0.0, 0, 'copie de la valeur observée sept jours plus tôt'))
rows.append(('Persistance', 0, 0.0, 0, 'copie de la dernière valeur observée'))

out = pd.DataFrame(rows, columns=['modèle', 'nombre de paramètres estimés', "temps d'un ajustement (s)",
                                  'ajustements du protocole', 'remarques'])
out['machine'] = f"{platform.processor() or platform.machine()} ; Python {platform.python_version()} ; torch {torch.__version__}"
out.to_csv(ROOT / 'exports' / 'complexite_modeles.csv', index=False)
pd.set_option('display.width', 250)
pd.set_option('display.max_colwidth', 60)
print(out.drop(columns=['remarques', 'machine']).round(2).to_string())
