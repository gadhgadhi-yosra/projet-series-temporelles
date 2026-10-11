"""Crée WattIf_rendu.zip : rapport (PDF et Word), notebooks, données préparées, scripts, tests, dépendances,
README, annexe LLM, figures et résultats. Le dossier .venv, l'historique interne et les fichiers temporaires sont exclus.
Affiche la taille de l'archive (la limite d'une pièce jointe est d'environ 25 Mo).
"""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SORTIE = ROOT / 'WattIf_rendu.zip'
FICHIERS = ['README.md', 'requirements.txt', 'requirements-lstm-gru.txt', 'R_packages.txt', 'data/daily.csv',
            'rapport/rapport_final.pdf', 'rapport/rapport_final.docx', 'rapport/rapport_final.md']
DOSSIERS = ['scripts', 'tests', 'exports', 'forecasts', 'figures', 'rapport/annexe_llm']
EXCLUS = {'__pycache__', '.ipynb_checkpoints'}

chemins = [ROOT / f for f in FICHIERS] + sorted(ROOT.glob('*.ipynb')) + sorted((ROOT / 'rapport').glob('[0-9a]*.md'))
for dossier in DOSSIERS:
    chemins += [p for p in sorted((ROOT / dossier).rglob('*')) if p.is_file() and not (set(p.parts) & EXCLUS)
                and p.suffix != '.pyc']
manquants = [p for p in chemins if not p.exists()]
if manquants:
    raise FileNotFoundError('Fichiers absents : ' + ', '.join(str(p.relative_to(ROOT)) for p in manquants))

with zipfile.ZipFile(SORTIE, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in dict.fromkeys(chemins):
        z.write(p, arcname=str(Path('WattIf') / p.relative_to(ROOT)))
taille = SORTIE.stat().st_size / 1e6
print(f'{SORTIE.name} : {len(set(chemins))} fichiers, {taille:.1f} Mo', '(sous la limite de 25 Mo)' if taille < 25 else '(AU-DESSUS de 25 Mo)')
