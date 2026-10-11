"""Validation croisée temporelle (walk-forward à fenêtre croissante) pour LSTM, GRU, SARIMA et naïf saisonnier.

Section 4.1 du rapport. Chaque pli apprend sur [début de la série, date d'origine] puis prévoit les 56 jours
suivants par blocs de 7 jours, exactement comme le protocole du notebook 07 (mêmes réseaux, mêmes hyperparamètres,
mêmes entrées, normalisation sur la période d'apprentissage du pli, 5 graines, moyenne des 5 réseaux).
Tous les plis se situent dans l'apprentissage (jusqu'au 6 août 2025) : le test externe n'est jamais utilisé.
Nombre d'époques : celui retenu par arrêt anticipé dans le notebook 07 (exports/lstm_gru/configuration.json),
appliqué sans nouvel arrêt anticipé, car aucun pli ne dispose d'une validation indépendante de son test.

Sorties : exports/lstm_gru/cv_temporelle.csv (détail par pli), exports/lstm_gru/cv_temporelle_resume.csv,
          figures/lstm_gru/cv_temporelle.png
"""
import ast
import json
import time
import warnings
from copy import deepcopy
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from statsmodels.tsa.statespace.sarimax import SARIMAX

ROOT = Path(__file__).resolve().parent.parent
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)

# Hyperparamètres identiques au notebook 07 (cellule 1).
WINDOW, BLOCK, HIDDEN, BATCH = 28, 7, 32, 64
LEARNING_RATE, MAX_EPOCHS, PATIENCE = 1e-3, 40, 7
SEEDS = (42, 43, 44, 45, 46)
TEST_DAYS = 56  # 8 blocs de 7 jours, comme la validation interne du notebook 07

# Chargement des définitions du notebook 07 (réseau, normalisation, fenêtres, prévision par blocs, entraînement).
NAMES = {'RecurrentForecaster', 'Standardizer', 'network_inputs', 'training_set', 'forecast_blocks',
         'train_network', 'rmse', 'scores'}
notebook = json.loads((ROOT / '07_lstm_gru.ipynb').read_text(encoding='utf-8'))
nodes = []
for cell in notebook['cells']:
    if cell['cell_type'] == 'code':
        for node in ast.parse(''.join(cell['source'])).body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in NAMES:
                nodes.append(node)
assert {n.name for n in nodes} == NAMES
namespace = dict(np=np, torch=torch, nn=nn, DataLoader=DataLoader, TensorDataset=TensorDataset, deepcopy=deepcopy,
                 WINDOW=WINDOW, BLOCK=BLOCK, HIDDEN=HIDDEN, BATCH=BATCH, LEARNING_RATE=LEARNING_RATE,
                 MAX_EPOCHS=MAX_EPOCHS, PATIENCE=PATIENCE)
exec(compile(ast.Module(body=nodes, type_ignores=[]), '07_lstm_gru.ipynb', 'exec'), namespace)
Standardizer, train_network, forecast_blocks = (namespace[k] for k in ('Standardizer', 'train_network', 'forecast_blocks'))

data = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date']).set_index('date').asfreq('D')
y = data['conso_gwh'].to_numpy(dtype=float)
weekday = data.index.dayofweek.to_numpy()
calendar = np.column_stack([np.sin(2 * np.pi * weekday / 7), np.cos(2 * np.pi * weekday / 7),
                            data['ferie'].to_numpy(dtype=float)])  # mêmes entrées que le notebook 07
N_APPRENTISSAGE = int(len(data) * 0.9)  # 3 506 jours : tout ce qui suit reste dans l'apprentissage

config = json.loads((ROOT / 'exports' / 'lstm_gru' / 'configuration.json').read_text(encoding='utf-8'))
EPOCHS = {kind: config['direct'][kind]['epochs'] for kind in ('LSTM', 'GRU')}
selection = json.loads((ROOT / 'exports' / 'selection_avant_test.json').read_text(encoding='utf-8'))
SARIMA_SPEC = dict(order=tuple(selection['order']), seasonal_order=tuple(selection['seasonal_order']),
                   trend=selection['trend'], enforce_stationarity=True, enforce_invertibility=True)

# (date de fin d'apprentissage du pli, saison du test) : 3 plis d'hiver et 2 plis d'été.
PLIS = [('2021-12-19', 'hiver'), ('2022-12-18', 'hiver'), ('2023-06-11', 'été'), ('2024-12-15', 'hiver'),
        ('2025-06-11', 'été')]


def metrics(obs, pred):
    e = np.asarray(pred) - np.asarray(obs)
    return {'RMSE': float(np.sqrt(np.mean(e ** 2))), 'MAE': float(np.mean(np.abs(e))),
            'MAPE (%)': float(100 * np.mean(np.abs(e / obs)))}


def sarima_folds(end, stop):
    """SARIMA estimé sur [0, end), puis prévisions par blocs de 7 jours à paramètres fixes."""
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        fitted = SARIMAX(y[:end], **SARIMA_SPEC).fit(disp=False, maxiter=500)
        converge = bool(fitted.mle_retvals.get('converged', False))
        preds, res = [], fitted
        for s in range(end, stop, BLOCK):
            preds.extend(np.asarray(res.get_forecast(min(BLOCK, stop - s)).predicted_mean))
            res = res.append(y[s:s + BLOCK], refit=False)
    return np.asarray(preds), converge


rows = []
for number, (end_date, saison) in enumerate(PLIS, start=1):
    end = data.index.get_loc(pd.Timestamp(end_date)) + 1
    stop = end + TEST_DAYS
    assert stop <= N_APPRENTISSAGE, 'un pli déborde sur le test externe'
    obs = y[end:stop]
    info = {'pli': number, 'saison du test': saison, 'fin apprentissage': data.index[end - 1].date(),
            'début test': data.index[end].date(), 'fin test': data.index[stop - 1].date(), 'jours apprentissage': end}
    scaler = Standardizer(y[:end])
    scaled = scaler.transform(y)
    for kind in ('LSTM', 'GRU'):
        t0 = time.perf_counter()
        preds = []
        for seed, epochs in zip(SEEDS, EPOCHS[kind]):
            model, _, _ = train_network(kind, scaled, calendar, end, seed, epochs=epochs)
            preds.append(scaler.inverse(forecast_blocks(model, scaled, calendar, end, stop)))
        rows.append({**info, 'modèle': kind, **metrics(obs, np.mean(preds, axis=0)),
                     'temps de calcul du pli (s)': time.perf_counter() - t0, 'convergence': ''})
    t0 = time.perf_counter()
    pred, ok = sarima_folds(end, stop)
    rows.append({**info, 'modèle': 'SARIMA', **metrics(obs, pred), 'temps de calcul du pli (s)': time.perf_counter() - t0,
                 'convergence': 'oui' if ok else 'non'})
    naive = y[end - 7:stop - 7]  # prévision = valeur observée sept jours plus tôt
    rows.append({**info, 'modèle': 'Naïf saisonnier', **metrics(obs, naive), 'temps de calcul du pli (s)': 0.0, 'convergence': ''})
    print(f'Pli {number} terminé : ' + ', '.join(f"{r['modèle']} {r['RMSE']:.1f}" for r in rows[-4:]), flush=True)

detail = pd.DataFrame(rows)
detail.to_csv(ROOT / 'exports' / 'lstm_gru' / 'cv_temporelle.csv', index=False)
resume = (detail.groupby('modèle')[['RMSE', 'MAE', 'MAPE (%)']].agg(['mean', 'std']))
resume.columns = [f'{a} ({b})' for a, b in resume.columns]
hiver = detail[detail['saison du test'] == 'hiver'].groupby('modèle')['RMSE'].mean().rename('RMSE moyen des plis d\'hiver')
ete = detail[detail['saison du test'] == 'été'].groupby('modèle')['RMSE'].mean().rename('RMSE moyen des plis d\'été')
rangs = (detail.assign(rang=detail.groupby('pli')['RMSE'].rank()).groupby('modèle')['rang'].mean().rename('rang moyen (1 = meilleur)'))
resume = resume.join([hiver, ete, rangs])
resume.to_csv(ROOT / 'exports' / 'lstm_gru' / 'cv_temporelle_resume.csv')

fig, ax = plt.subplots(figsize=(9, 3.8))
width = 0.2
order = ['LSTM', 'GRU', 'SARIMA', 'Naïf saisonnier']
colors = {'LSTM': '#eda100', 'GRU': '#1baf7a', 'SARIMA': '#2a78d6', 'Naïf saisonnier': '#898781'}
labels = [f"Pli {p}\n{s}\n{d[:7]}" for p, (d, s) in enumerate(PLIS, start=1)]
labels = [f"Pli {i}\n{PLIS[i-1][1]} ({detail[detail['pli'] == i]['début test'].iloc[0]:%m/%Y})" for i in range(1, len(PLIS) + 1)]
for k, m in enumerate(order):
    vals = detail[detail['modèle'] == m].sort_values('pli')['RMSE']
    ax.bar(np.arange(len(PLIS)) + (k - 1.5) * width, vals, width, label=m, color=colors[m])
ax.set_xticks(np.arange(len(PLIS)))
ax.set_xticklabels(labels)
ax.set_ylabel('RMSE (GWh/jour)')
ax.set_title('Validation croisée temporelle : RMSE sur 56 jours par pli')
ax.legend(ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.22), frameon=False)
fig.tight_layout()
fig.savefig(ROOT / 'figures' / 'lstm_gru' / 'cv_temporelle.png', dpi=150)
pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 30)
print(detail.round(2).to_string())
print(resume.round(2).to_string())
