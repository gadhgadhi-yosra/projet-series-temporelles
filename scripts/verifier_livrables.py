"""Vérifier dates, chiffres, provenance, notebook et livraison sans réestimer."""
from pathlib import Path
import os
import tempfile
os.environ.setdefault('MPLCONFIGDIR', os.path.join(tempfile.gettempdir(), 'wattif-matplotlib'))
import json
import hashlib
import zipfile
import numpy as np
import pandas as pd
import nbformat
from statsmodels.tsa.statespace.sarimax import SARIMAX

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
checks = []
n = nbformat.read('arima_sarima.ipynb', as_version=4)
nbformat.validate(n)
for i, c in enumerate(n.cells):
    if c.cell_type == 'code':
        compile(c.source, f'cell_{i}', 'exec')
        assert c.execution_count is not None, f'Cellule non exécutée : {i}'
        assert not any(o.output_type == 'error' for o in c.outputs)
checks.append('Notebook valide : toutes les cellules de code exécutées sans sortie d’erreur.')
for record in json.loads(Path('docs/import_fayfa.json').read_text())['fichiers']:
    assert hashlib.sha256(Path(record['fichier']).read_bytes()).hexdigest() == record['sha256']
checks.append('Les 17 fichiers importés de Fayfa sont inchangés.')
meta = json.loads(Path('exports/metadonnees_previsions.json').read_text())
selection = json.loads(Path('exports/selection_avant_test.json').read_text())
assert meta['modele'] == selection['modele']
assert meta['sha256_donnees'] == hashlib.sha256(Path('data/daily.csv').read_bytes()).hexdigest()
comp = pd.read_csv('exports/comparaison_validation_complete.csv').set_index('modele')
assert comp.loc[meta['modele'], 'RMSE'] == comp.loc[~comp.index.str.startswith('naif_'), 'RMSE'].min()
checks.append('Modèle final identique au choix fondé sur la RMSE interne.')
forecast = pd.read_csv('exports/previsions_7j.csv', parse_dates=['date'])
assert forecast.date.tolist() == list(pd.date_range('2026-09-01', periods=7, freq='D'))
assert np.isfinite(forecast.iloc[:, 1:]).all().all()
assert (forecast.borne_inferieure_95 <= forecast.prevision).all()
assert (forecast.prevision <= forecast.borne_superieure_95).all()
y = pd.read_csv('data/daily.csv', index_col='date', parse_dates=True).conso_gwh.asfreq('D')
params = pd.read_csv('exports/parametres_modele_final.csv').estimation.to_numpy()
reconstructed = SARIMAX(y, order=tuple(meta['order']), seasonal_order=tuple(meta['seasonal_order']),
                        trend=meta['trend'], enforce_stationarity=True,
                        enforce_invertibility=True).filter(params).get_forecast(7)
np.testing.assert_allclose(reconstructed.predicted_mean, forecast.prevision, rtol=1e-8)
np.testing.assert_allclose(reconstructed.conf_int().to_numpy(), forecast.iloc[:, 2:].to_numpy(), rtol=1e-8)
checks.append('Les 7 prévisions et leurs bornes sont reproduites à partir des paramètres sauvegardés.')
pred = pd.read_csv('exports/predictions_test.csv', parse_dates=['date','origine'])
scores = pd.read_csv('exports/scores_test.csv').set_index('modele')
assert (pred.date > pred.origine).all()
assert ((pred.date - pred.origine).dt.days == pred.horizon).all()
assert pred.horizon.between(1, 7).all()
for name, group in pred.groupby('modele'):
    assert len(group) == 390
    assert group.date.is_unique
    assert group.date.tolist() == list(pd.date_range('2025-08-07','2026-08-31'))
    err = group.prevision - group.observe
    np.testing.assert_allclose(scores.loc[name, ['MAE','RMSE']].to_numpy(),
                               [err.abs().mean(), np.sqrt((err**2).mean())])
    if name == meta['modele']:
        covered = ((group.observe >= group.borne_inferieure_95) & (group.observe <= group.borne_superieure_95)).mean()
        np.testing.assert_allclose(covered, scores.loc[name,'couverture_95'])
        assert group.groupby('horizon').size().tolist() == [56,56,56,56,56,55,55]
checks.append('Les 1 170 prévisions de test, horizons, métriques et couverture sont cohérents.')
for f in ['predictions_validation_interne.csv','predictions_validation_complement.csv']:
    frame = pd.read_csv(Path('exports') / f, parse_dates=['date','origine'])
    assert (frame.date > frame.origine).all()
    assert frame.date.max() < pd.Timestamp('2025-08-07')
checks.append('Toutes les prévisions de validation précèdent le test externe.')
context = json.loads(Path('rapport/annexe_llm/contexte_resultats.json').read_text())
assert context['identifiant'] == meta['modele']
np.testing.assert_allclose(context['test']['scores'][0]['RMSE'], scores.loc[meta['modele'],'RMSE'])
manifest = json.loads(Path('rapport/annexe_llm/manifest.json').read_text())
for name, checksum in manifest['empreintes_sha256'].items():
    assert hashlib.sha256((Path('rapport/annexe_llm')/name).read_bytes()).hexdigest() == checksum
checks.append('Contexte et empreintes des prompts/réponses LLM vérifiés.')
manifest = json.loads(Path('livraison_anas/manifest.json').read_text())
for name, checksum in manifest.items():
    assert hashlib.sha256((Path('livraison_anas')/name).read_bytes()).hexdigest() == checksum
assert Path('livraison_anas/previsions_7j.csv').read_bytes() == Path('exports/previsions_7j.csv').read_bytes()
with zipfile.ZipFile('livraison_anas.zip') as z:
    assert z.testzip() is None
    for name in manifest:
        assert z.read('livraison_anas/' + name) == (Path('livraison_anas')/name).read_bytes()
checks.append('ZIP de livraison intact et identique aux exports vérifiés.')
Path('docs/verification_finale.md').write_text('# Vérification finale\n\n' + '\n'.join('- ' + line for line in checks) +
    '\n\nTrois tests automatisés de la validation glissante sont disponibles dans `tests/test_previsions.py`. '
    'Ces vérifications portent sur le fonctionnement et la cohérence des livrables ; elles ne prouvent pas les hypothèses statistiques du modèle.\n')
print('\n'.join(checks))
