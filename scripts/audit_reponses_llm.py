"""Vérifications chiffrées utilisées pour l'audit des réponses du LLM (section 5.6).

1. Chaque nombre cité dans une réponse est recherché dans le prompt correspondant ; les nombres absents du prompt
   sont listés (ce sont soit des valeurs calculées par le LLM, soit des erreurs) : exports/audit_llm_nombres.csv.
2. Des mesures complémentaires, tirées des prévisions du test, servent à juger les affirmations générales du LLM
   (couverture par horizon et par saison, part des jours sous la RMSE, tests contre la persistance) :
   exports/audit_llm_verifications.csv.
3. Les mesures propres à la réponse de ChatGPT au prompt (b) (06_reponse_chatgpt.md) sont ajoutées à la suite du même
   fichier : moyenne du test, erreur médiane, part des jours prévus à 4 % près, couverture et largeur des intervalles
   de chaque modèle, coût du protocole, tests des modèles classiques contre les références.
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
          ('05_prompt_c_recommandations_gestion.txt', '05_reponse_integrale.md'),
          ('04_prompt_b_vulgarisation_decideur.txt', '06_reponse_chatgpt.md')]  # même prompt (b), soumis à ChatGPT


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
# --- Mesures complémentaires pour l'audit de la réponse de ChatGPT (prompt b)
moy_test = float(g['observe'].mean())
ea = g['erreur'].abs()
ep = 100 * ea / g['observe']
v.append(('Consommation moyenne observée sur le test (GWh/jour)', moy_test))
v.append(('RMSE d\'AR-GARCH rapportée à la consommation moyenne du test (%)', 100 * rmse / moy_test))
v.append(('AR-GARCH : erreur absolue médiane (GWh/jour)', float(ea.median())))
v.append(('AR-GARCH : erreur absolue médiane en pourcentage de la consommation du jour (%)', float(ep.median())))
v.append(('AR-GARCH : part des jours prévus à 4 % près (%)', 100 * float((ep <= 4).mean())))
v.append(('AR-GARCH : part des jours prévus à 4 % près, hiver (décembre à février) (%)', 100 * float((ep[hiver] <= 4).mean())))
v.append(('AR-GARCH : part des jours prévus à 4 % près, hors hiver (%)', 100 * float((ep[~hiver] <= 4).mean())))
carres = (g['erreur'] ** 2).sort_values(ascending=False)
v.append(('AR-GARCH : part de l\'erreur quadratique totale due aux 10 % de jours les plus mal prévus (%)',
          100 * float(carres.iloc[:len(g) // 10].sum() / carres.sum())))
v.append(('AR-GARCH : part de l\'erreur quadratique totale due aux jours d\'hiver (%)',
          100 * float((g.loc[hiver, 'erreur'] ** 2).sum() / carres.sum())))
temp = pd.read_csv(ROOT / 'data' / 'daily.csv', parse_dates=['date'])[['date', 'temp_moy']]
gt = g.merge(temp, on='date')
pires = gt.reindex(gt['erreur'].abs().sort_values(ascending=False).index).head(12)
v.append(('AR-GARCH : nombre de surestimations parmi les 12 plus fortes erreurs du test', float((pires['erreur'] > 0).sum())))
v.append(('AR-GARCH : température moyenne des jours de surestimation parmi ces 12 erreurs (°C)', float(pires.loc[pires['erreur'] > 0, 'temp_moy'].mean())))
v.append(('AR-GARCH : température moyenne des jours de sous-estimation parmi ces 12 erreurs (°C)', float(pires.loc[pires['erreur'] < 0, 'temp_moy'].mean())))
gh = gt[gt['date'].dt.month.isin([12, 1, 2])]
v.append(('AR-GARCH : corrélation entre erreur signée et température, hiver', float(np.corrcoef(gh['erreur'], gh['temp_moy'])[0, 1])))

# Intervalles à 95 % de chaque modèle qui en fournit : couverture, écart au niveau annoncé, largeur
sarima = pd.read_csv(ROOT / 'exports' / 'predictions_test.csv', parse_dates=['date'])
sarima = sarima[sarima['modele'] == 'SARIMA_211_011']
for nom, t in [('SARIMA', sarima), ('VAR(3)', d[d['modele'] == 'var']), ('VECM', d[d['modele'] == 'vecm']),
               ('AR-GARCH', g), ('Prophet', d[d['modele'] == 'prophet'])]:
    dans = (t['observe'] >= t['borne_inferieure_95']) & (t['observe'] <= t['borne_superieure_95'])
    h = t['date'].dt.month.isin([12, 1, 2])
    v.append((f'{nom} : couverture de l\'intervalle à 95 % (%)', 100 * float(dans.mean())))
    v.append((f'{nom} : écart absolu entre la couverture et 95 % (points)', abs(100 * float(dans.mean()) - 95)))
    v.append((f'{nom} : nombre de jours hors de l\'intervalle (19,5 attendus sur 390)', float((~dans).sum())))
    v.append((f'{nom} : couverture en hiver (%)', 100 * float(dans[h].mean())))
    v.append((f'{nom} : largeur moyenne de l\'intervalle (GWh/jour)', float((t['borne_superieure_95'] - t['borne_inferieure_95']).mean())))

# Coût du protocole : temps d'un ajustement multiplié par le nombre d'ajustements
cx = pd.read_csv(ROOT / 'exports' / 'complexite_modeles.csv').set_index('modèle')
for nom in ['LSTM', 'GRU', 'Prophet']:
    v.append((f'{nom} : temps d\'ajustement du protocole, tous ajustements compris (s)',
              float(cx.loc[nom, "temps d'un ajustement (s)"] * cx.loc[nom, 'ajustements du protocole'])))

# Modèles statistiques classiques contre les références et contre les réseaux
classiques = ['AR-GARCH(1,2)-t', 'VAR(3)', 'SARIMA', 'VECM(12, r=1)']
references = ['Persistance', 'Naïf saisonnier', 'Prophet']
paires = dm[(dm['modèle A'].isin(classiques) & dm['modèle B'].isin(references))
            | (dm['modèle B'].isin(classiques) & dm['modèle A'].isin(references))]
for perte in ['quadratique', 'absolue']:
    v.append((f'Modèles classiques contre références : paires significatives après Holm, perte {perte} (sur {len(paires)})',
              float((paires[f'p Holm ({perte})'] < 0.05).sum())))
    for ref in references:
        sub = paires[(paires['modèle A'] == ref) | (paires['modèle B'] == ref)]
        v.append((f'Modèles classiques significativement meilleurs que {ref} après Holm, perte {perte} (sur 4)',
                  float((sub[f'p Holm ({perte})'] < 0.05).sum())))
rmse_test = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'comparaison_test.csv').set_index('modele')['RMSE']
v.append(('Modèles classiques dont la RMSE de test dépasse celles du LSTM et du GRU (sur 4)',
          float((rmse_test[classiques] > rmse_test[['LSTM', 'GRU']].max()).sum())))
cv = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'cv_temporelle.csv').pivot(index='pli', columns='modèle', values='RMSE')
for reseau in ['GRU', 'LSTM']:
    v.append((f'Validation croisée : plis où le {reseau} a une RMSE inférieure à celle du SARIMA (sur 5)',
              float((cv[reseau] < cv['SARIMA']).sum())))
pd.DataFrame(v, columns=['mesure', 'valeur']).to_csv(ROOT / 'exports' / 'audit_llm_verifications.csv', index=False)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 100)
print(pd.DataFrame(v, columns=['mesure', 'valeur']).round(3).to_string(index=False))
