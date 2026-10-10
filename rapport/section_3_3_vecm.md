# 3.3 — Test de Johansen et modèle à correction d'erreur (VECM)

Texte préparé avec assistance IA à partir des calculs du projet, le 9 octobre 2026. Résultats reproductibles dans `05_var_vecm_garch_prophet.ipynb`.

## Principe

Deux séries intégrées d'ordre 1 (I(1)) sont **cointégrées** si une combinaison linéaire est stationnaire : elles peuvent dériver séparément mais restent liées par un équilibre de long terme. Le test de Johansen estime le rang r de cointégration (ici entre 0 et 2). Si r = 1, le VECM écrit la variation des séries comme une correction de l'écart à l'équilibre (terme α·β′y) plus une dynamique de court terme. Si r = 2 (rang plein), les séries sont déjà stationnaires.

## Résultat du test de Johansen

Sur les données brutes (constante, 2 retards en différences, choisis par BIC) :

| H0 | Trace | Seuil 95 % | Rejet |
| --- | --- | --- | --- |
| r ≤ 0 | 337,7 | 15,5 | oui |
| r ≤ 1 | 39,6 | 3,8 | oui |

Le **rang est 2 (rang plein)**. Le résultat est identique avec 1 à 13 retards, avec constante ou tendance, et sur des séries corrigées du calendrier (trace 577,7 et 178,3). Le seul cas donnant r = 1 est la spécification sans constante sur données brutes, inadaptée (consommation moyenne de 1 254 GWh).

**Interprétation.** Un rang plein signifie que les deux séries sont stationnaires, ce que l'ADF avait déjà montré (section 3.2). Il n'y a pas de tendance stochastique commune, donc pas de cointégration au sens strict ; un VAR en niveaux est la spécification cohérente.

## VECM estimé (rang 1 imposé)

Le sujet demande un VECM. Nous l'estimons avec r = 1 en signalant que ce choix est **imposé et non soutenu par le test**. Le calendrier est introduit en exogène à court terme. Le nombre de retards en différences est choisi par la même règle que le VAR (RMSE de validation interne) parmi 2, 8 et 12, qui sont les ordres de BIC, HQIC et AIC.

| k (retards en différences) | RMSE validation (GWh) |
| --- | --- |
| 2 | 55,48 |
| 8 | 62,37 |
| 12 | 53,44 |

Le modèle retenu est **VECM(k = 12, r = 1)**, estimé sur l'apprentissage complet.

- **Relation d'équilibre** : conso + 82,1 × température = constante, soit environ −82 GWh/jour par °C à long terme.
- **Vitesse de correction** : α_conso = −0,0181 (p = 0,004). Environ **1,8 % de l'écart à l'équilibre est résorbé chaque jour**, soit une **demi-vie d'environ 38 jours** (ln 0,5 / ln(1 − 0,0181)). Le signe est cohérent : un écart positif entraîne une baisse ultérieure de la consommation.
- α_temp = −0,0023 est significatif mais sans sens physique (la consommation ne pilote pas la météo) : artefact de la relation imposée.
- Le terme de correction est stationnaire (ADF p = 0,0003), ce qui est attendu quand les deux séries le sont déjà et ne prouve pas la cointégration.

## Robustesse de la vitesse de correction

| k | α_conso | p | Demi-vie (jours) | β_température |
| --- | --- | --- | --- | --- |
| 2 | −0,052 | < 0,001 | 13 | 61,8 |
| 8 | +0,007 | 0,028 | aucune correction | 134,1 |
| 12 | −0,018 | 0,004 | 38 | 82,1 |

La vitesse de correction change de signe selon le nombre de retards et β varie du simple au double. Elle ne doit donc être lue que comme un ordre de grandeur (de quelques jours à plusieurs semaines), pas comme une valeur précise.

## Diagnostics

Équation de consommation : Ljung-Box p ≈ 10⁻¹⁶ (h = 7), Jarque-Bera p ≈ 10⁻²⁶⁰ (kurtosis 5,77), ARCH-LM p ≈ 10⁻²⁶. Équation de température : pas d'autocorrélation résiduelle (p ≈ 1), queues légèrement épaisses. Mêmes défauts que le VAR.

## Performance sur le test externe

**RMSE 87,56 GWh, MAE 58,71, MAPE 4,61 %**, biais −7,2 GWh, couverture 91,3 % (largeur 294 GWh). Le VECM est moins précis que le VAR(3) (78,96) et que le SARIMA (82,38). Une explication plausible, non testée ici, est que le rang 1 imposé et les 12 retards contraignent le modèle sans bénéfice. Prévisions : `forecasts/vecm.csv` ; prévision à 7 jours : `exports/ghada/previsions_7j_vecm.csv`.

## Limites

Le VECM suppose des séries I(1) cointégrées, hypothèse contredite par les tests. Son interprétation économique (équilibre, vitesse de correction) est donc fragile. Pour une vraie question de cointégration, il faudrait des variables non stationnaires (par exemple des séries de production cumulées ou des niveaux de prix de l'énergie), hors du périmètre de ce projet.
