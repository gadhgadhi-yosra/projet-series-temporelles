# 5 — IA générative et LLM

Cette section évalue l'usage d'un LLM comme outil d'aide à l'analyse, selon les quatre points du sujet : hypothèses de modèles à partir des statistiques descriptives (5.2), explication vulgarisée (5.3), recommandations de gestion avec limites explicites (5.4), comparaison avec nos résultats et recherche des erreurs du LLM (5.5 et 5.6). Les prompts et les réponses intégrales sont en annexe B.

## 5.1 Démarche et outil utilisé

**LLM consulté : Claude (Anthropic), modèle Claude Opus 5.5 (identifiant `claude-opus-5-5`), le 11 octobre 2026.** Trois prompts complets lui ont été soumis ; ils sont générés à partir des fichiers de résultats par `scripts/preparer_prompts_llm.py` : (a) hypothèses de modèles à partir des statistiques descriptives, (b) vulgarisation de la comparaison finale pour un décideur, (c) recommandations de gestion du réseau, avec limites formulées par le LLM. Chaque prompt demande de n'utiliser que les chiffres fournis.

Trois précisions s'imposent sur la portée de cet exercice.

- **Le LLM n'était pas neutre vis-à-vis du projet.** Claude a aussi servi d'outil d'aide pendant la préparation du projet (code, mise en forme). Chaque réponse est rédigée à partir du seul contenu de son prompt, mais ce n'est pas la consultation d'un outil qui découvrirait le sujet.
- **L'audit n'est pas indépendant.** La vérification de la section 5.6 a été menée avec le même outil, de façon systématique : chaque nombre cité est recherché dans le prompt par un script (`scripts/audit_reponses_llm.py`), et chaque affirmation générale est confrontée à un fichier de résultats.
- **Un premier tour exploratoire** (9 octobre 2026, deux prompts sur le seul SARIMA, autre outil identifié dans `rapport/annexe_llm/manifest.json`) est conservé en annexe B ; il n'entre pas dans l'analyse ci-dessous.

## 5.2 Hypothèses de modèles à partir des statistiques descriptives

[[TAB:stats|Statistiques descriptives transmises au LLM (apprentissage, 3 506 jours)|La consommation est asymétrique à droite et plus aplatie qu'une loi normale ; la série brute est stationnaire à la limite, ses différences le sont nettement.]]

| Série | Moyenne | Variance | Écart-type | Skewness | Kurtosis excédentaire | ADF (statistique ; p) | KPSS (statistique ; p) |
|---|---|---|---|---|---|---|---|
| Consommation (GWh/jour) | 1 258,93 | 63 882,41 | 252,75 | 0,69 | −0,43 | −4,10 ; 0,001 | 0,40 ; 0,076 |
| Consommation, différence simple | −0,09 | 7 160,41 | 84,62 | 0,44 | 0,44 | −12,21 ; < 0,001 | 0,02 ; > 0,10 |
| Consommation, différences simple et saisonnière | −0,11 | 3 601,69 | 60,01 | 0,08 | 2,52 | −18,40 ; < 0,001 | 0,01 ; > 0,10 |
| Température moyenne (°C) | 13,34 | 37,91 | 6,16 | 0,05 | −0,94 | −3,48 ; 0,009 | 0,08 ; > 0,10 |

À partir de ces seules statistiques (prompt a), le LLM propose :

- **Différenciation** : d = 1, D = 1, s = 7 comme choix prudent, à comparer à d = 0 ou D = 0, en notant que l'ADF et le KPSS ne testent pas une racine unitaire saisonnière ;
- **SARIMA de période 7** : (0,1,1)(0,1,1)[7], (1,1,1)(0,1,1)[7] et (1,1,0)(0,1,1)[7], les ordres devant être confirmés par l'ACF et la PACF ;
- **Régression dynamique** avec température et calendrier, la forme du lien restant à vérifier ;
- **VAR en niveaux** sur la consommation et la température, sans VECM si les séries sont stationnaires ;
- **GARCH(1,1)**, puis loi de Student et ordres supérieurs si un effet ARCH subsiste, motivé par le kurtosis de 2,52 des variations ;
- **LSTM ou GRU** de petite taille (fenêtre de 7 à 28 jours), validés par walk-forward ;
- les **références naïves** et un modèle à saisonnalités multiples si un cycle annuel est confirmé.

Ces hypothèses recoupent largement la démarche du projet. Deux écarts sont à relever : le modèle finalement retenu, SARIMA(2,1,1)(0,1,1)[7], n'est pas dans la liste, et le LLM qualifie la structure hebdomadaire de « forte » alors que c'est la saisonnalité annuelle qui domine (force de 0,90 contre 0,45), ce que les statistiques transmises ne lui permettaient pas de voir.

## 5.3 Explication vulgarisée pour un décideur

À partir du tableau de comparaison et des tests de Diebold–Mariano (prompt b), le LLM explique qu'AR-GARCH a la plus petite erreur (74,45 GWh/jour, « environ 6 % » de la consommation moyenne), qu'une erreur plus petite n'est pas une supériorité démontrée, et que le choix doit aussi tenir compte des intervalles, de la lisibilité et du coût. Extrait :

> « Deux modèles peuvent avoir des erreurs différentes sur une année simplement par hasard. Le test de Diebold–Mariano mesure si l'écart est trop grand pour être dû au hasard. […] On ne peut pas dire qu'il sera encore le meilleur l'an prochain : le test porte sur une seule période de 390 jours, et l'écart avec ses concurrents directs n'est pas démontré. »

L'explication est fidèle aux chiffres et rend bien la distinction entre « meilleur observé » et « meilleur démontré ». Elle dépasse la longueur demandée (environ 400 mots) et lisse trois points : la couverture de 95,9 % est une moyenne qui masque l'hiver, « les modèles qui tiennent compte du passé récent » ne battent pas tous la persistance de façon significative, et le coût des réseaux est sous-estimé (section 5.6).

## 5.4 Recommandations de gestion et limites

Le prompt (c) demande des recommandations à partir des prévisions du 1er au 7 septembre 2026, en invitant le LLM à formuler lui-même leurs limites. Il en propose six : (1) utiliser AR-GARCH comme référence et raisonner sur son intervalle ; (2) dimensionner la marge de sécurité sur la borne haute de l'intervalle (de 1 128,01 GWh le 1er septembre à 1 186,42 GWh le 7) et refaire la prévision chaque jour, l'erreur passant de 37,9 à 96,2 GWh/jour entre les horizons 1 et 7 ; (3) placer les opérations de maintenance le dimanche, jour de creux (de 906,98 à 938,23 GWh selon les modèles) ; (4) surveiller les jours où les modèles divergent ; (5) écarter Prophet et les méthodes naïves ; (6) garder un réseau de neurones en parallèle.

**Limites formulées par le LLM.** Le témoin fait aussi bien qu'AR-GARCH en précision ; la couverture de 95,9 % est une moyenne qui ne vaut pas forcément pour chaque saison ; un intervalle à 95 % laisse un jour sur vingt en dehors ; des modèles d'accord entre eux peuvent se tromper ensemble ; rien ne permet d'anticiper une vague de froid ; le niveau de marge acceptable dépend de la capacité disponible et du coût d'une défaillance, absents des données.

**Limites que nous ajoutons.**

- **La marge du LLM est insuffisante en hiver.** Sur le test, la couverture d'AR-GARCH tombe à 91,11 % de décembre à février (contre 97,33 % le reste de l'année), et sa RMSE y atteint 121,62 GWh/jour (contre 52,62) ; la plus forte erreur est de 329,35 GWh le 14 janvier 2026. Une marge calée sur la borne haute serait donc dépassée environ un jour sur onze en hiver, précisément quand le réseau est tendu.
- **La semaine prévue est une semaine facile.** Début septembre, les modèles s'accordent à moins de 35 GWh/jour près ; ces recommandations ne disent rien de leur comportement lors d'un épisode de froid, que la validation croisée montre environ quatre fois plus difficile à prévoir (section 4.1).
- **Le choix d'AR-GARCH n'est pas démontré.** Aucun test corrigé ne le distingue de ses concurrents ; il n'a pas été soumis à la validation croisée, contrairement au SARIMA et aux réseaux.
- **Les données de 2026 sont consolidées**, donc révisables, et les valeurs réelles de septembre ne sont pas disponibles : aucune de ces recommandations n'a pu être confrontée à la réalité.
- **Les recommandations restent génériques** : sans capacité disponible, sans coût d'une défaillance ni prévision météo, le LLM ne peut proposer aucun seuil chiffré de marge. Elles ne constituent pas une aide à la décision d'exploitation.

## 5.5 Comparaison entre nos résultats et les réponses du LLM

Le sujet demande de comparer l'explication du LLM à une interprétation experte rédigée avant de le solliciter. **Aucune interprétation personnelle n'a été rédigée avant la consultation du LLM** ; cette exigence n'est donc pas satisfaite, et nous ne la reconstituons pas après coup. La comparaison ci-dessous porte sur **les résultats calculés du projet** (sections 2 à 7) contre les réponses du LLM.

- **Convergences.** Différenciation d = 1, D = 1, s = 7 ; VAR en niveaux et absence de cointégration (rang plein de Johansen) ; loi de Student pour le GARCH (ν ≈ 4,10) ; petit réseau à une couche ; distinction entre meilleur observé et meilleur démontré ; rôle du GARCH limité aux intervalles ; rejet de Prophet à sept jours.
- **Divergences.** Le LLM ne propose pas le modèle retenu, SARIMA(2,1,1)(0,1,1)[7] ; il part d'un GARCH(1,1), que nos diagnostics jugent insuffisant (effet ARCH résiduel, p = 4 × 10⁻⁵), tout en prévoyant de monter en ordre ; il ne peut pas voir que la saisonnalité annuelle domine.
- **Simplifications excessives.** Neuf affirmations sur 29 sont exactes mais incomplètes (tableau @tab:audit) ; les plus importantes concernent la couverture moyenne, qui masque l'hiver, et la marge de sécurité qui en découle.
- **Causalités non fondées.** Nous n'en relevons aucune : la seule explication causale avancée (le creux du week-end lié à la baisse d'activité) est présentée comme une hypothèse non démontrée.

## 5.6 Audit des affirmations du LLM

Nous avons relevé 29 affirmations chiffrées ou causales dans les trois réponses et confronté chacune à un fichier du projet (audit complet en annexe B et dans `rapport/annexe_llm/audit_gabarit.csv`). **Résultat : 20 affirmations correctes, 9 simplifiées, aucune fausse, aucune causalité non fondée.** Sur les 170 nombres cités, 156 figurent dans le prompt ; les 14 autres sont des seuils usuels, des ordres de modèle ou des valeurs que le LLM calcule et signale comme telles (toutes recalculées et exactes).

[[TAB:audit|Affirmations du LLM jugées simplifiées|Aucune affirmation n'est fausse, mais neuf sont incomplètes ; les plus lourdes de conséquences portent sur la couverture en hiver.]]

| Réponse | Affirmation du LLM | Fichier de vérification | Correction |
|---|---|---|---|
| a | La baisse de variance après Δ7 signale une structure hebdomadaire forte | `02_eda.ipynb` | Force saisonnière hebdomadaire de 0,45 contre 0,90 pour le cycle annuel |
| a | Trois candidats SARIMA proposés | `exports/comparaison_validation_complete.csv` | Le modèle retenu, SARIMA(2,1,1)(0,1,1)[7], n'est pas proposé |
| a | L'asymétrie suggère une variable externe explicative | `02_eda.ipynb` | Le lien avec la température (−0,83) vient de l'analyse exploratoire, pas de l'asymétrie |
| b | AR-GARCH n'est distingué d'aucun concurrent direct | `exports/lstm_gru/diebold_mariano_toutes_paires.csv` | En perte absolue, le VECM est à la limite du seuil (0,053) |
| b | Les modèles à mémoire battent nettement la persistance | `exports/audit_llm_verifications.csv` | Vrai pour six modèles sur huit ; pas pour le VECM (0,230) ni Prophet (1,000) |
| b | AR-GARCH atteint la couverture annoncée (95,9 %) | `exports/audit_llm_verifications.csv` | 91,11 % en hiver contre 97,33 % le reste de l'année |
| b | Tous les temps de calcul sont faibles | `exports/complexite_modeles.csv` | Temps à multiplier par 5 pour les réseaux et par 56 pour Prophet |
| c | AR-GARCH est le seul modèle avec intervalle | `exports/previsions_7j.csv` | Vrai dans le prompt ; quatre autres modèles en fournissent (annexe A) |
| c | Marge sur la borne haute, un jour sur vingt en dehors | `exports/audit_llm_verifications.csv` | Environ un jour sur onze en dehors en hiver |

**Lecture critique de ce résultat.** L'absence d'erreur chiffrée ne prouve pas la fiabilité du LLM en général : tous les chiffres étaient fournis dans le prompt, avec la consigne de n'en citer aucun autre. Les faiblesses observées sont d'une autre nature : le LLM généralise une moyenne (couverture, coût), ne peut pas voir ce qui n'est pas dans le prompt (saisonnalité annuelle, dégradation hivernale) et reste général quand la décision demande un seuil.

## 5.7 Apport et limites du LLM

**Ce qu'il a apporté.** Un cadrage rapide et structuré : en une réponse, la liste des familles de modèles à tester, avec pour chacune le diagnostic à faire, recoupe la démarche du projet. Une vulgarisation claire de notions difficiles à transmettre (erreur quadratique, intervalle à 95 %, différence non significative). Des limites formulées spontanément et justes (un seul test, accord entre modèles qui n'est pas une mesure de fiabilité). Nous n'avons pas mesuré le temps gagné.

**Ce qu'il n'a pas su faire.** Trouver le modèle retenu, qui exigeait l'ACF, la PACF et une validation. Voir ce que les statistiques transmises ne contenaient pas : la saisonnalité annuelle dominante, les ruptures de 2020 et 2022, la dégradation des intervalles en hiver. Chiffrer une marge de sécurité. Vérifier ses propres affirmations : tout le contrôle repose sur les fichiers du projet. Il ne remplace donc ni les calculs, ni les diagnostics, ni la relecture critique de chaque chiffre.
