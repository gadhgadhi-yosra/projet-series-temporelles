"""Prépare les trois prompts complets du second tour LLM (section 5) à partir des fichiers de résultats.

Sorties dans rapport/annexe_llm/ :
    03_prompt_a_hypotheses_modeles.txt, 04_prompt_b_vulgarisation_decideur.txt, 05_prompt_c_recommandations_gestion.txt.
Aucun appel à un LLM : les prompts sont à soumettre à l'outil choisi ; chaque réponse intégrale est enregistrée telle quelle
dans 03_reponse_integrale.md, 04_reponse_integrale.md et 05_reponse_integrale.md, puis auditée (audit_gabarit.csv).
Tous les chiffres viennent des fichiers exports/ ; ils ne sont jamais saisis à la main.
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'rapport' / 'annexe_llm'


def fr(x, d=2):
    """Format français : virgule décimale, espace pour les milliers."""
    return f'{x:,.{d}f}'.replace(',', ' ').replace('.', ',')


# --- Statistiques descriptives (prompt a)
st = pd.read_csv(ROOT / 'exports' / 'stats_descriptives.csv')
lignes = []
for _, r in st.iterrows():
    lignes.append(
        f"- {r['série']} ({r['unité']}) : n = {int(r['observations'])} ; moyenne = {fr(r['moyenne'])} ; variance = {fr(r['variance'])} ; "
        f"écart-type = {fr(r['écart-type'])} ; minimum = {fr(r['minimum'])} ; maximum = {fr(r['maximum'])} ; "
        f"skewness = {fr(r['asymétrie (skewness)'])} ; kurtosis excédentaire = {fr(r['aplatissement excédentaire (kurtosis)'])} ; "
        f"ADF : statistique = {fr(r['ADF statistique'])}, p-value = {r['ADF p-value']:.4f} ; "
        f"KPSS : statistique = {fr(r['KPSS statistique'])}, p-value = {r['KPSS p-value']:.4f}".replace('.', ','))
stats_txt = '\n'.join(lignes)

PROMPT_A = f"""Tu es statisticien, spécialiste des séries temporelles. Je prépare un mini-projet sur la consommation électrique quotidienne de la France métropolitaine (RTE éCO2mix), en GWh par jour, du 1er janvier 2016 au 6 août 2025 (3 506 jours consécutifs, période d'apprentissage). Je dispose aussi de la température moyenne nationale (°C), du jour de la semaine et des jours fériés. Le but est de prévoir la consommation à sept jours.

Voici les statistiques descriptives de la série (la différence simple est Δ1 ; la différence saisonnière est de période 7 jours ; KPSS avec constante ; ADF avec choix des retards par AIC) :

{stats_txt}

Ta mission : à partir uniquement de ces statistiques, propose des hypothèses de modèles à tester.
1. Pour chaque famille de modèles que tu proposes (par exemple SARIMA, VAR, GARCH, réseaux de neurones récurrents…), indique les ordres ou réglages plausibles et la statistique précise ci-dessus qui motive l'hypothèse.
2. Indique les choix de différenciation (d, D) et leur justification, en discutant le fait que l'ADF et le KPSS ne concordent pas forcément.
3. Pour chaque hypothèse, précise ce que ces statistiques ne permettent PAS de conclure et quel diagnostic complémentaire il faudrait faire.
4. Si tu cites un chiffre, il doit figurer dans les données ci-dessus ; si une information te manque, dis-le au lieu de la supposer.
Réponds en français, de façon structurée."""

# --- Résultats de comparaison (prompts b et c)
comp = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'comparaison_test.csv')
gm = pd.read_csv(ROOT / 'exports' / 'ghada' / 'metriques_test.csv', index_col=0)
cplx = pd.read_csv(ROOT / 'exports' / 'complexite_modeles.csv').set_index('modèle')
couv = {'AR-GARCH(1,2)-t': 'AR-GARCH(1,2)-t', 'VAR(3)': 'VAR(3)', 'SARIMA': 'SARIMA_211_011 (Yosra)',
        'VECM(12, r=1)': 'VECM(k=12, r=1)', 'Prophet': 'Prophet (hebdo)'}
cle_cplx = {'AR-GARCH(1,2)-t': 'AR-GARCH(1,2)-t', 'LSTM': 'LSTM', 'GRU': 'GRU', 'VAR(3)': 'VAR(3)', 'SARIMA + LSTM': 'SARIMA + LSTM',
            'SARIMA': 'SARIMA(2,1,1)(0,1,1)[7]', 'VECM(12, r=1)': 'VECM(12, r = 1)', 'Prophet': 'Prophet',
            'Persistance': 'Persistance', 'Naïf saisonnier': 'Naïf saisonnier'}
tab = []
for _, r in comp.iterrows():
    nom = r['modele']
    c = f"{gm.loc[couv[nom], 'couverture_95'] * 100:.1f} %".replace('.', ',') if nom in couv else 'sans intervalle'
    cx = cplx.loc[cle_cplx[nom]]
    temps = cx["temps d'un ajustement (s)"]
    tab.append(f"- {nom} : RMSE = {fr(r['RMSE'])}, MAE = {fr(r['MAE'])}, MAPE = {fr(r['MAPE (%)'])} %, couverture de l'intervalle à 95 % = {c}, "
               f"paramètres = {int(cx['nombre de paramètres estimés'])}, temps d'un ajustement = {fr(temps)} s")
t = gm.loc['AR[1,2,7,8,14] variance constante (témoin)']
tab.append(f"- Témoin AR à variance constante : RMSE = {fr(t['RMSE'])}, MAE = {fr(t['MAE'])}, MAPE = {fr(t['MAPE (%)'])} %, couverture = {fr(t['couverture_95'] * 100, 1)} %")
tableau = '\n'.join(tab)

dm = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'diebold_mariano_toutes_paires.csv')
dm = dm[dm['modèle A'] == 'AR-GARCH(1,2)-t']
dm_txt = '\n'.join(
    f"- AR-GARCH contre {r['modèle B']} : p brute (perte quadratique) = {fr(r['p (quadratique)'], 3)} ; p corrigée de Holm, perte quadratique = "
    f"{fr(r['p Holm (quadratique)'], 3)} ; p corrigée de Holm, perte absolue = {fr(r['p Holm (absolue)'], 4)}" for _, r in dm.iterrows())

prev = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'previsions_7j.csv')
g = {m: pd.read_csv(ROOT / 'exports' / 'ghada' / f'previsions_7j_{m}.csv') for m in ('garch', 'var', 'vecm', 'prophet')}
lp = []
for i, r in prev.iterrows():
    lp.append(f"- {r['date']} ({r['jour']}) : SARIMA = {fr(r['SARIMA'])} ; SARIMA + LSTM = {fr(r['SARIMA + LSTM'])} ; LSTM = {fr(r['LSTM'])} ; "
              f"GRU = {fr(r['GRU'])} ; AR-GARCH = {fr(g['garch'].prevision[i])} [intervalle à 95 % : {fr(g['garch'].borne_inferieure_95[i])} à "
              f"{fr(g['garch'].borne_superieure_95[i])}] ; VAR = {fr(g['var'].prevision[i])} ; VECM = {fr(g['vecm'].prevision[i])} ; "
              f"Prophet = {fr(g['prophet'].prevision[i])}")
previsions = '\n'.join(lp)
hor = pd.read_csv(ROOT / 'exports' / 'lstm_gru' / 'rmse_par_horizon.csv')
hor_txt = ' ; '.join(f"horizon {i + 1} : {fr(v, 1)}" for i, v in enumerate(hor['AR-GARCH(1,2)-t']))

CONTEXTE = """Contexte : consommation électrique quotidienne de la France (GWh/jour). Les modèles ont été ajustés sur 3 506 jours (du 1er janvier 2016 au 6 août 2025) et évalués sur un test de 390 jours (du 7 août 2025 au 31 août 2026), par blocs de 7 jours (horizons de 1 à 7 jours). Aucun modèle n'utilise de prévision météo. Erreurs en GWh/jour ; la MAPE est en pourcentage. Prophet est réajusté chaque semaine, les autres modèles gardent des paramètres fixes ; l'hybride SARIMA + LSTM est évalué avec des erreurs d'apprentissage pseudo hors échantillon."""

PROMPT_B = f"""Tu es un analyste qui doit expliquer des résultats statistiques à un décideur non statisticien (par exemple un responsable de la planification d'un gestionnaire de réseau électrique). Ce lecteur ne connaît ni la RMSE, ni les tests statistiques.

{CONTEXTE}

Résultats sur le test (dix modèles) :
{tableau}

Test de Diebold–Mariano (il compare deux modèles sur la perte moyenne de chaque bloc de 7 jours ; p corrigée = p-value corrigée des comparaisons multiples par la méthode de Holm sur 45 paires de modèles ; une p corrigée supérieure à 0,05 signifie qu'on ne peut pas affirmer que les deux modèles diffèrent) :
{dm_txt}

Ta mission : rédige une explication en français, sans jargon inutile, d'environ 400 mots, qui :
1. dise quel modèle a la plus petite erreur et ce qu'une erreur de {fr(comp['RMSE'].min())} GWh par jour (RMSE) veut dire concrètement pour une consommation journalière moyenne de {fr(st['moyenne'].iloc[0])} GWh ;
2. explique la différence entre une erreur plus petite et une supériorité démontrée, à partir du test de Diebold–Mariano ;
3. compare les modèles sur la précision, la qualité des intervalles, la lisibilité et le coût de calcul ;
4. indique ce qu'on peut et ne peut pas conclure.
N'utilise que les chiffres ci-dessus ; si une information manque, dis-le."""

PROMPT_C = f"""Tu es conseiller en gestion de réseau électrique. À partir des prévisions ci-dessous, propose des recommandations de gestion (par exemple anticipation d'un pic de consommation, dimensionnement d'une marge de sécurité, choix du modèle à utiliser au quotidien).

{CONTEXTE}

Prévisions de consommation du 1er au 7 septembre 2026 (GWh/jour ; la dernière observation disponible est celle du 31 août 2026) :
{previsions}

Erreur de test d'AR-GARCH(1,2)-t selon l'horizon (RMSE, GWh/jour) : {hor_txt}.
Précision générale sur le test : voir le tableau suivant.
{tableau}

Ta mission :
1. Donne des recommandations de gestion concrètes et priorisées, chacune reliée à un chiffre ci-dessus.
2. Formule toi-même, pour chaque recommandation, ses limites et ses risques (hypothèses non vérifiées, erreurs possibles, ce qui pourrait la rendre fausse).
3. Indique explicitement ce que ces données ne permettent pas de décider.
Réponds en français, de façon structurée. Ne présente aucune causalité comme démontrée si elle ne l'est pas par les données fournies."""

fichiers = {'03_prompt_a_hypotheses_modeles.txt': PROMPT_A, '04_prompt_b_vulgarisation_decideur.txt': PROMPT_B,
            '05_prompt_c_recommandations_gestion.txt': PROMPT_C}
for nom, texte in fichiers.items():
    (OUT / nom).write_text(texte + '\n', encoding='utf-8', newline='\n')
    print('écrit', nom, len(texte.split()), 'mots')
