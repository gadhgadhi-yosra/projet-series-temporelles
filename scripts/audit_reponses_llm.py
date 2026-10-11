"""Vérifications chiffrées utilisées pour l'audit des réponses du LLM (section 5.6).

1. Chaque nombre cité dans une réponse est recherché dans le prompt correspondant ; les nombres absents du prompt
   sont listés (ce sont soit des valeurs calculées par le LLM, soit des erreurs) : exports/audit_llm_nombres.csv.
2. Des mesures complémentaires, tirées des prévisions du test, servent à juger les affirmations générales du LLM
   (couverture par horizon et par saison, part des jours sous la RMSE, tests contre la persistance) :
   exports/audit_llm_verifications.csv.
Aucun appel à un LLM : le script ne fait que lire les fichiers du projet.
"""
from pathlib import Path
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / 'rapport' / 'annexe_llm'
PAIRES = [('03_prompt_a_hypotheses_modeles.txt', '03_reponse_integrale.md'),
          ('04_prompt_b_vulgarisation_decideur.txt', '04_reponse_integrale.md'),
          ('05_prompt_c_recommandations_gestion.txt', '05_reponse_integrale.md')]


def nombres(texte):
    """Nombres au format français (1 258,93 ; -4,10 ; 0,0005 ; 390), signe moins typographique accepté."""
    t = texte.replace(' ', ' ').replace(' ', ' ').replace('−', '-')
    trouves = re.findall(r'(?<![\w,])-?\d{1,3}(?: \d{3})+(?:,\d+)?|(?<![\w,])-?\d+(?:,\d+)?', t)
    return [x.replace(' ', '') for x in trouves]


lignes = []
for prompt, reponse in PAIRES:
    dans_prompt = set(nombres((A / prompt).read_text(encoding='utf-8')))
    # un nombre du prompt peut être cité avec moins de zéros finaux (0,0010 -> 0,001) : on compare les valeurs
    valeurs_prompt = {float(x.replace(',', '.')) for x in dans_prompt}
    for x in nombres((A / reponse).read_text(encoding='utf-8')):
        v = float(x.replace(',', '.'))
        lignes.append({'réponse': reponse, 'nombre': x, 'présent dans le prompt': v in valeurs_prompt or abs(v) in valeurs_prompt})
nb = pd.DataFrame(lignes)
nb.to_csv(ROOT / 'exports' / 'audit_llm_nombres.csv', index=False)
print(nb.groupby('réponse')['présent dans le prompt'].agg(['size', 'sum']))
print('Nombres absents du prompt (valeurs calculées ou générales) :')
print(nb[~nb['présent dans le prompt']].drop_duplicates().to_string(index=False))

# --- Mesures complémentaires sur le test (AR-GARCH)
d = pd.read_csv(ROOT / 'exports' / 'ghada' / 'predictions_test_detail.csv', parse_dates=['date'])
g = d[d['modele'] == 'garch'].copy()
g['erreur'] = g['prevision'] - g['observe']
g['dans'] = (g['observe'] >= g['borne_inferieure_95']) & (g['observe'] <= g['borne_superieure_95'])
rmse = float(np.sqrt((g['erreur'] ** 2).mean()))
v = [('AR-GARCH : RMSE recalculée sur le test (GWh/jour)', rmse),
     ('AR-GARCH : part des jours dont l\'erreur absolue est inférieure à la RMSE (%)', 100 * float((g['erreur'].abs() < rmse).mean())),
     ('AR-GARCH : couverture globale de l\'intervalle à 95 % (%)', 100 * float(g['dans'].mean()))]
for h, sub in g.groupby('horizon'):
    v.append((f'AR-GARCH : couverture à l\'horizon {h} (%)', 100 * float(sub['dans'].mean())))
hiver = g['date'].dt.month.isin([12, 1, 2])
for nom, masque in [('hiver (décembre à février)', hiver), ('hors hiver', ~hiver)]:
    sub = g[masque]
    v.append((f'AR-GARCH : RMSE {nom} (GWh/jour)', float(np.sqrt((sub['erreur'] ** 2).mean()))))
    v.append((f'AR-GARCH : couverture {nom} (%)', 100 * float(sub['dans'].mean())))
    v.append((f'AR-GARCH : nombre de jours {nom}', float(len(sub))))
v.append(('AR-GARCH : plus forte erreur absolue du test (GWh/jour)', float(g['erreur'].abs().max())))
v.append(('AR-GARCH : date de la plus forte erreur absolue (aaaammjj)', float(g.loc[g['erreur'].abs().idxmax(), 'date'].strftime('%Y%m%d'))))
dm = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'diebold_mariano_toutes_paires.csv')
pers = dm[(dm['modèle A'] == 'Persistance') | (dm['modèle B'] == 'Persistance')]
v.append(('Modèles significativement meilleurs que la persistance après Holm, perte quadratique (sur 9)', float((pers['p Holm (quadratique)'] < 0.05).sum())))
for _, r in pers.iterrows():
    autre = r['modèle A'] if r['modèle B'] == 'Persistance' else r['modèle B']
    v.append((f'{autre} contre persistance : p corrigée, perte quadratique', float(r['p Holm (quadratique)'])))
st = pd.read_csv(ROOT / 'exports' / 'stats_descriptives.csv')
v.append(('Rapport des variances : brute / différence simple', float(st['variance'][0] / st['variance'][1])))
v.append(('Rapport des variances : différence simple / différences simple et saisonnière', float(st['variance'][1] / st['variance'][2])))
v.append(('RMSE d\'AR-GARCH rapportée à la consommation moyenne (%)', 100 * rmse / float(st['moyenne'][0])))
pd.DataFrame(v, columns=['mesure', 'valeur']).to_csv(ROOT / 'exports' / 'audit_llm_verifications.csv', index=False)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 100)
print(pd.DataFrame(v, columns=['mesure', 'valeur']).round(3).to_string(index=False))
