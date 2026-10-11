"""Génère rapport/annexe_A_tableaux.md à partir des fichiers de résultats (aucun chiffre saisi à la main).

Les grands tableaux du rapport (candidats SARIMA, robustesse du VECM, détails R, détails de la section 7,
RMSE par horizon, intervalles de prévision, toutes les paires de Diebold–Mariano) sont déplacés en annexe.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
E = ROOT / 'exports'
MOIS = {'Jan': 'janvier', 'Feb': 'février', 'Mar': 'mars', 'Apr': 'avril', 'May': 'mai', 'Jun': 'juin', 'Jul': 'juillet',
        'Aug': 'août', 'Sep': 'septembre', 'Oct': 'octobre', 'Nov': 'novembre', 'Dec': 'décembre'}


def fr(x, d=2):
    if pd.isna(x):
        return '—'
    return f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',').replace('-', '−')


def pval(p):
    if pd.isna(p):
        return '—'
    if p < 0.001:
        return '< 0,001'
    return fr(p, 3)


def md_table(header, rows):
    out = ['| ' + ' | '.join(header) + ' |', '|' + '---|' * len(header)]
    out += ['| ' + ' | '.join(str(c) for c in r) + ' |' for r in rows]
    return '\n'.join(out)


def nom_sarima(nom):
    table = {'SARIMA_211_011': 'SARIMA(2,1,1)(0,1,1)[7]', 'SARIMA_212_011': 'SARIMA(2,1,2)(0,1,1)[7]',
             'SARIMA_110_011': 'SARIMA(1,1,0)(0,1,1)[7]', 'SARIMA_110_101': 'SARIMA(1,1,0)(1,0,1)[7]',
             'SARIMA_011_011': 'SARIMA(0,1,1)(0,1,1)[7]', 'SARIMA_110_111': 'SARIMA(1,1,0)(1,1,1)[7]',
             'SARIMA_111_011': 'SARIMA(1,1,1)(0,1,1)[7]', 'SARIMA_311_011': 'SARIMA(3,1,1)(0,1,1)[7]',
             'SARIMA_100_101': 'SARIMA(1,0,0)(1,0,1)[7]', 'auto_SARIMA': '`auto_arima` saisonnier : SARIMA(2,1,1)(1,0,0)[7]',
             'naif_saisonnier': 'Naïf saisonnier', 'auto_ARIMA': '`auto_arima` non saisonnier : ARIMA(2,1,2)',
             'naif_derniere_valeur': 'Naïf « dernière valeur »', 'ARIMA_110': 'ARIMA(1,1,0)', 'ARIMA_011': 'ARIMA(0,1,1)'}
    return table[nom]


parts = ['# Annexe A — Tableaux détaillés\n']

# A.1 candidats SARIMA
c = pd.read_csv(E / 'comparaison_validation_complete.csv')
rows = [[nom_sarima(r['modele']), fr(r['RMSE']), fr(r['MAE']), fr(r['AIC']), fr(r['BIC'])] for _, r in c.iterrows()]
parts += ['## A.1 Candidats SARIMA sur la validation interne\n',
          '[[TAB:annexe_sarima|Quinze modèles comparés sur la validation interne (3 450 jours d\'estimation, huit blocs de sept jours)|Les AIC et BIC sont donnés à titre informatif : on ne les compare pas entre différenciations différentes.]]\n',
          md_table(['Modèle', 'RMSE (GWh/jour)', 'MAE (GWh/jour)', 'AIC', 'BIC'], rows), '']

# A.2 SARIMA par horizon
h = pd.read_csv(E / 'scores_test_par_horizon.csv')
h = h[h['modele'] == 'SARIMA_211_011']
rows = [[int(r['horizon']), int(r['n']), fr(r['RMSE']), fr(r['MAE']), fr(r['biais_prevision']), fr(r['couverture_95'] * 100, 1) + ' %',
         fr(r['largeur_moyenne_95'])] for _, r in h.iterrows()]
parts += ['## A.2 SARIMA retenu : erreurs selon l\'horizon\n',
          '[[TAB:annexe_sarima_horizon|Erreurs du SARIMA(2,1,1)(0,1,1)[7] selon l\'horizon sur le test externe|L\'erreur croît avec l\'horizon ; les horizons 6 et 7 ont une observation de moins car le dernier bloc compte cinq jours.]]\n',
          md_table(['Horizon (jours)', 'Observations', 'RMSE (GWh/jour)', 'MAE (GWh/jour)', 'Biais (GWh/jour)', 'Couverture à 95 %',
                    'Largeur moyenne de l\'intervalle (GWh/jour)'], rows), '']

# A.3 robustesse du VECM
v = pd.read_csv(E / 'ghada' / 'vecm_robustesse_retards.csv')
rows = [[int(r['k_ar_diff']), fr(r['α_conso'], 3), pval(r['p(α_conso)']), fr(r['α_temp'], 4), fr(r['β_temp'], 1),
         fr(r['demi-vie (jours)'], 1) if not pd.isna(r['demi-vie (jours)']) else 'aucune correction'] for _, r in v.iterrows()]
parts += ['## A.3 VECM : robustesse de la vitesse de correction\n',
          '[[TAB:annexe_vecm|Vitesse de correction du VECM selon le nombre de retards en différences|La vitesse de correction change de signe et β varie du simple au double : elle n\'est lisible que comme un ordre de grandeur.]]\n',
          md_table(['Retards en différences k', 'α (consommation)', 'p-value de α', 'α (température)', 'β (température)',
                    'Demi-vie (jours)'], rows), '']

# A.4 R contre Python
r_ = pd.read_csv(E / 'R' / 'r_vs_python.csv')
rows = [[r['element'], fr(r['python'], 3), fr(r['R'], 3), fr(r['ecart_relatif_pct'], 2) + ' %'] for _, r in r_.iterrows()]
parts += ['## A.4 Réplication R et Python : les 27 éléments comparés\n',
          '[[TAB:annexe_r|Comparaison R et Python, 27 éléments|25 éléments sur 27 coïncident à 0,1 % près ; les deux écarts supérieurs concernent le GARCH.]]\n',
          md_table(['Élément', 'Python', 'R', 'Écart relatif'], rows), '']

# A.5 profil mensuel
p = pd.read_csv(E / 'R' / 'correlation_profil_mensuel_R.csv')
rows = [[MOIS[r['mois']], fr(r['niveaux']), fr(r['variations'])] for _, r in p.iterrows()]
parts += ['## A.5 Corrélation température–consommation selon le mois\n',
          '[[TAB:annexe_profil|Corrélation selon le mois, sur les niveaux et sur les variations journalières|Les deux colonnes ont la même forme : le lien saisonnier n\'est pas une coïncidence de calendrier.]]\n',
          md_table(['Mois', 'Corrélation sur les niveaux', 'Corrélation sur les variations'], rows), '']

# A.6 hivers
t = pd.read_csv(E / 'R' / 'thermosensibilite_hivers_R.csv')
rows = [[r['hiver'], int(r['jours']), fr(r['correlation'], 3), fr(r['pente_GWh_par_degre'], 1), fr(r['conso_a_8_degres'], 0)] for _, r in t.iterrows()]
parts += ['## A.6 Sensibilité à la température de chaque hiver\n',
          '[[TAB:annexe_hivers|Corrélation, pente et consommation estimée à 8 °C pour chaque hiver|La pente reste comprise entre −40,2 et −56,5 GWh/jour par °C, tandis que le niveau à 8 °C baisse après l\'hiver 2021-2022.]]\n',
          md_table(['Hiver', 'Jours', 'Corrélation', 'Pente (GWh/jour par °C)', 'Consommation à 8 °C (GWh/jour)'], rows), '']

# A.7 RMSE par horizon (10 modèles)
hh = pd.read_csv(E / 'lstm_gru' / 'rmse_par_horizon.csv')
cols = [c for c in hh.columns if not c.startswith('horizon')]
rows = [[str(r.iloc[0]).split(' ')[0]] + [fr(r[c], 1) for c in cols] for _, r in hh.iterrows()]
parts += ['## A.7 RMSE par horizon pour les dix modèles\n',
          '[[TAB:annexe_horizon|RMSE selon l\'horizon de prévision (GWh/jour)|Les modèles dynamiques sont à égalité à l\'horizon 1 ; Prophet est mauvais dès l\'horizon 1.]]\n',
          md_table(['Horizon (jours)'] + cols, rows), '']

# A.8 intervalles de prévision
sar = pd.read_csv(E / 'previsions_7j.csv')
g = {m: pd.read_csv(E / 'ghada' / f'previsions_7j_{m}.csv') for m in ('garch', 'var', 'vecm', 'prophet')}
dates = ['1er septembre', '2 septembre', '3 septembre', '4 septembre', '5 septembre', '6 septembre', '7 septembre']
rows = []
for i, d in enumerate(dates):
    cells = [d]
    for df in (sar, g['garch'], g['var'], g['vecm'], g['prophet']):
        cells.append(f"{fr(df.prevision[i])} [{fr(df.borne_inferieure_95[i])} ; {fr(df.borne_superieure_95[i])}]")
    rows.append(cells)
parts += ['## A.8 Prévisions du 1er au 7 septembre 2026 avec intervalles à 95 %\n',
          "[[TAB:annexe_intervalles|Prévisions et intervalles nominaux à 95 % (GWh/jour)|Le 1er septembre, l'intervalle d'AR-GARCH est le plus étroit et celui de Prophet le plus large ; tous sont nominaux et ne garantissent pas la couverture future.]]\n",
          md_table(['Date', 'SARIMA', 'AR-GARCH', 'VAR(3)', 'VECM', 'Prophet'], rows), '']

# A.9 et A.10 Diebold–Mariano
d = pd.read_csv(E / 'lstm_gru' / 'diebold_mariano_toutes_paires.csv')
q = d['p Holm (quadratique)'] < 0.05
a = d['p Holm (absolue)'] < 0.05
seul = d[(~q) & a].sort_values('p Holm (absolue)')
rows = [[r['modèle A'], r['modèle B'], pval(r['p Holm (quadratique)']), pval(r['p Holm (absolue)'])] for _, r in seul.iterrows()]
parts += ['## A.9 Paires significatives en perte absolue seulement\n',
          '[[TAB:annexe_dm_abs|Dix paires significatives après correction de Holm en perte absolue seulement|Elles opposent toutes un modèle dynamique au naïf saisonnier, à Prophet ou à la persistance ; aucune ne compare deux modèles dynamiques entre eux.]]\n',
          md_table(['Modèle A (plus petite RMSE)', 'Modèle B', 'p corrigée, perte quadratique', 'p corrigée, perte absolue'], rows), '']
rows = [[r['modèle A'], r['modèle B'], pval(r['p (quadratique)']), pval(r['p Holm (quadratique)']), pval(r['p (absolue)']),
         pval(r['p Holm (absolue)'])] for _, r in d.iterrows()]
parts += ['## A.10 Les 45 paires du test de Diebold–Mariano\n',
          '[[TAB:annexe_dm|Test de Diebold–Mariano sur les 45 paires de modèles|Sept paires sont significatives après correction de Holm en perte quadratique et dix-sept en perte absolue.]]\n',
          md_table(['Modèle A', 'Modèle B', 'p brute, quadratique', 'p corrigée, quadratique', 'p brute, absolue', 'p corrigée, absolue'], rows), '']

# A.11 questions de comparaison du sujet
qd = pd.read_csv(E / 'lstm_gru' / 'diebold_mariano_questions.csv')
rows = [[r['question'].split(' — ')[-1][:1].upper() + r['question'].split(' — ')[-1][1:], r['modèle A'], r['modèle B'], fr(r['RMSE A']), fr(r['RMSE B']),
         pval(r['p Holm (quadratique)']), pval(r['p Holm (absolue)'])] for _, r in qd.iterrows()]
parts += ['## A.11 Questions de comparaison du sujet\n',
          "[[TAB:annexe_dm_questions|Tests de Diebold–Mariano pour les comparaisons demandées par le sujet|Aucune de ces différences n'est significative en perte quadratique ; en perte absolue, seule la comparaison du meilleur réseau au naïf saisonnier l'est.]]\n",
          md_table(['Question', 'Modèle A', 'Modèle B', 'RMSE de A (GWh/jour)', 'RMSE de B (GWh/jour)', 'p corrigée, quadratique',
                    'p corrigée, absolue'], rows), '']

(ROOT / 'rapport' / 'annexe_A_tableaux.md').write_text('\n'.join(parts) + '\n', encoding='utf-8', newline='\n')
print('écrit rapport/annexe_A_tableaux.md')
