"""Exécute réellement le notebook et conserve les sorties même en cas d'échec.

Usage depuis la racine : python scripts/executer_lstm_gru.py
Le noyau utilise exactement le Python qui lance ce script.
"""
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache' / 'lstm_gru'
if (CACHE / 'notebook_tools').exists():
    sys.path.insert(0, str(CACHE / 'notebook_tools'))
for directory in ('matplotlib', 'jupyter', 'ipython'):
    (CACHE / directory).mkdir(parents=True, exist_ok=True)
os.environ.update({
    'MPLCONFIGDIR': str(CACHE / 'matplotlib'),
    'JUPYTER_RUNTIME_DIR': str(CACHE / 'jupyter'),
    'IPYTHONDIR': str(CACHE / 'ipython'),
    'MPLBACKEND': 'module://matplotlib_inline.backend_inline',
    'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1',
})

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

path = ROOT / '07_lstm_gru.ipynb'
notebook = nbformat.read(path, as_version=4)
nbformat.validate(notebook)
for cell in notebook.cells:
    if cell.cell_type == 'code':
        cell.outputs = []
        cell.execution_count = None

started = time.perf_counter()


def save():
    nbformat.write(notebook, path)


def cell_start(cell, cell_index, **kwargs):
    if cell.cell_type == 'code':
        title = cell.source.splitlines()[0][:90] if cell.source else ''
        print(f'Cellule {cell_index + 1}/{len(notebook.cells)} : {title}', flush=True)


def cell_done(cell, cell_index, **kwargs):
    save()
    for output in cell.get('outputs', []):
        if output.output_type == 'stream':
            print(output.text[-3000:], end='', flush=True)


manager = KernelManager(kernel_name='python3')
manager.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
client = NotebookClient(notebook, km=manager, timeout=3600,
                        resources={'metadata': {'path': str(ROOT)}},
                        on_cell_start=cell_start, on_cell_executed=cell_done,
                        record_timing=True, allow_errors=False)
try:
    client.execute(cwd=str(ROOT), cleanup_kc=True)
finally:
    save()
nbformat.validate(notebook)
code = [cell for cell in notebook.cells if cell.cell_type == 'code']
assert all(cell.execution_count is not None for cell in code)
assert not any(output.output_type == 'error' for cell in code for output in cell.outputs)
print(f'EXÉCUTION RÉUSSIE : {len(code)} cellules de code, {time.perf_counter() - started:.1f} s.', flush=True)
