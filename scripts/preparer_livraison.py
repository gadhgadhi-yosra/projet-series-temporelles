"""Assembler la livraison sans envoyer de message ni publier de fichiers."""
from pathlib import Path
import shutil
import zipfile
import json
import hashlib

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'exports'
DEST = ROOT / 'livraison_anas'
DEST.mkdir(exist_ok=True)
for name in ['previsions_7j.csv', 'metadonnees_previsions.json', 'scores_test.csv']:
    shutil.copy2(OUT / name, DEST / name)
shutil.copy2(ROOT / 'figures/arima_sarima/previsions_7j.png', DEST / 'previsions_7j.png')
meta = json.loads((OUT / 'metadonnees_previsions.json').read_text())
(DEST / 'README.md').write_text(f'''# Prévisions à intégrer — WattIf

Modèle : SARIMA{tuple(meta['order'])}{tuple(meta['seasonal_order'][:3])}[7].

- Cible : consommation électrique quotidienne `conso_gwh`.
- Unité : **GWh/jour** pour toutes les colonnes numériques du CSV de prévisions.
- Dernière observation : **31 août 2026**.
- Dates prévues : **1er–7 septembre 2026** (ne pas les remplacer par des dates d'octobre).
- CSV UTF-8, séparateur virgule, point décimal, dates ISO `YYYY-MM-DD`, sans index.
- Colonnes : `date`, `prevision`, `borne_inferieure_95`, `borne_superieure_95`.
- Bornes : intervalles de prévision gaussiens nominaux à 95 %, conditionnels au modèle. Leur couverture future n'est pas garantie.

Les diagnostics résiduels restent défavorables ; cette limite doit accompagner la présentation. Les données réelles de septembre ne sont pas présentes dans le CSV source. Les prévisions ne constituent pas une comparaison déjà observée avec ces valeurs réelles.

`scores_test.csv` décrit le test historique du 7 août 2025 au 31 août 2026, en blocs successifs de sept jours (dernier bloc de cinq), avec paramètres fixes et états actualisés. Le modèle n'a pas été sélectionné à partir des erreurs de ce test. Les métadonnées contiennent les ordres, le protocole et l'empreinte des données.

Ce dossier est prêt à transmettre manuellement. Aucun envoi automatique n'a été effectué.
''')
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.iterdir()) if p.is_file() and p.name != 'manifest.json'}
(DEST / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
with zipfile.ZipFile(ROOT / 'livraison_anas.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(DEST.iterdir()):
        if p.is_file(): z.write(p, arcname='livraison_anas/' + p.name)
print('livraison_anas.zip créé, sans envoi.')
