"""Courbes de perte d'apprentissage et de validation du LSTM et du GRU (section 4.1).

Le notebook 07 ne sauvegarde que la RMSE de validation par époque. Ce script réentraîne, avec les mêmes définitions,
les mêmes hyperparamètres et la graine 42, un LSTM et un GRU sur les 3 450 premiers jours (entrées : consommation
et calendrier) et enregistre à chaque époque la perte d'apprentissage et la RMSE de validation (56 jours, blocs de
7 jours). Aucun arrêt anticipé n'est appliqué ici : on trace les 40 époques pour voir où la validation cesse de
progresser, et on repère l'époque retenue par le notebook (exports/lstm_gru/configuration.json).
Sorties : exports/lstm_gru/courbes_perte.csv, figures/lstm_gru/courbes_perte_train_validation.png
"""
import ast
import json
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

ROOT = Path(__file__).resolve().parent.parent
torch.set_num_threads(1)
torch.use_deterministic_algorithms(True)
WINDOW, BLOCK, HIDDEN, BATCH, LEARNING_RATE, MAX_EPOCHS, PATIENCE = 28, 7, 32, 64, 1e-3, 40, 7
SEED = 42

NAMES = {'RecurrentForecaster', 'Standardizer', 'network_inputs', 'training_set', 'forecast_blocks', 'rmse'}
notebook = json.loads((ROOT / '07_lstm_gru.ipynb').read_text(encoding='utf-8'))
nodes = [node for cell in notebook['cells'] if cell['cell_type'] == 'code'
         for node in ast.parse(''.join(cell['source'])).body
         if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in NAMES]
ns = dict(np=np, torch=torch, nn=nn, DataLoader=DataLoader, TensorDataset=TensorDataset, deepcopy=deepcopy, WINDOW=WINDOW,
          BLOCK=BLOCK, HIDDEN=HIDDEN, BATCH=BATCH, LEARNING_RATE=LEARNING_RATE, MAX_EPOCHS=MAX_EPOCHS, PATIENCE=PATIENCE)
exec(compile(ast.Module(body=nodes, type_ignores=[]), '07_lstm_gru.ipynb', 'exec'), ns)

data = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date']).set_index('date').asfreq('D')
y = data['conso_gwh'].to_numpy(dtype=float)
weekday = data.index.dayofweek.to_numpy()
calendar = np.column_stack([np.sin(2 * np.pi * weekday / 7), np.cos(2 * np.pi * weekday / 7), data['ferie'].to_numpy(dtype=float)])
N_TRAIN = data.index.get_loc(pd.Timestamp('2025-06-11')) + 1
N_DEV = data.index.get_loc(pd.Timestamp('2025-08-06')) + 1
scaler = ns['Standardizer'](y[:N_TRAIN])
scaled = scaler.transform(y)
config = json.loads((ROOT / 'exports' / 'lstm_gru' / 'configuration.json').read_text(encoding='utf-8'))

rows = []
for kind in ('LSTM', 'GRU'):
    torch.manual_seed(SEED)
    model = ns['RecurrentForecaster'](kind, calendar.shape[1])
    loader = DataLoader(ns['training_set'](scaled, calendar, N_TRAIN), batch_size=BATCH, shuffle=True,
                        generator=torch.Generator().manual_seed(SEED))
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    retained = config['direct'][kind]['epochs'][0]  # époque retenue pour la graine 42 dans le notebook 07
    for epoch in range(1, MAX_EPOCHS + 1):
        model.train()
        losses = []
        for windows, calendars, targets in loader:
            optimizer.zero_grad()
            loss = nn.functional.mse_loss(model(windows, calendars), targets)
            loss.backward()
            optimizer.step()
            losses.append(loss.item() * len(targets))
        train_rmse = float(np.sqrt(sum(losses) / (N_TRAIN - WINDOW))) * scaler.std  # perte moyenne → RMSE en GWh/jour
        pred = scaler.inverse(ns['forecast_blocks'](model, scaled, calendar, N_TRAIN, N_DEV))
        rows.append({'modèle': kind, 'époque': epoch, 'RMSE apprentissage (GWh/jour)': train_rmse,
                     'RMSE validation (GWh/jour)': ns['rmse'](y[N_TRAIN:N_DEV], pred), 'époque retenue au notebook 07': retained})
        print(kind, epoch, round(train_rmse, 2), round(rows[-1]['RMSE validation (GWh/jour)'], 2), flush=True)

curves = pd.DataFrame(rows)
curves.to_csv(ROOT / 'exports' / 'lstm_gru' / 'courbes_perte.csv', index=False)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=True)
for axis, kind in zip(axes, ('LSTM', 'GRU')):
    c = curves[curves['modèle'] == kind]
    axis.plot(c['époque'], c['RMSE apprentissage (GWh/jour)'], label='apprentissage', color='#2a78d6')
    axis.plot(c['époque'], c['RMSE validation (GWh/jour)'], label='validation', color='#eb6834')
    axis.axvline(c['époque retenue au notebook 07'].iloc[0], color='#555', ls='--', lw=1)
    axis.set_title(f'{kind} (graine {SEED})')
    axis.set_xlabel('Époque')
axes[0].set_ylabel('RMSE (GWh/jour)')
axes[0].legend(frameon=False)
fig.suptitle("Perte d'apprentissage et de validation par époque (pointillé : époque retenue par arrêt anticipé)")
fig.tight_layout()
fig.savefig(ROOT / 'figures' / 'lstm_gru' / 'courbes_perte_train_validation.png', dpi=150)
