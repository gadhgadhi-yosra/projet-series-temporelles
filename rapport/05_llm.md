# 5 — IA générative et LLM

Cette section évalue l'usage d'un LLM comme outil d'aide à l'analyse, selon les quatre points du sujet : hypothèses de modèles à partir des statistiques descriptives (5.2), explication vulgarisée (5.3), recommandations de gestion avec limites explicites (5.4), comparaison avec une interprétation rédigée par le groupe et recherche des erreurs des LLM (5.5 et 5.6). Les prompts, les réponses intégrales et l'interprétation du groupe sont en annexe B.

## 5.1 Démarche et outils utilisés

**Premier tour : Claude (Anthropic), modèle Claude Opus 5.5 (identifiant `claude-opus-5-5`), le 11 octobre 2026.** Trois prompts complets lui ont été soumis ; ils sont générés à partir des fichiers de résultats par `scripts/preparer_prompts_llm.py` : (a) hypothèses de modèles à partir des statistiques descriptives, (b) vulgarisation de la comparaison finale pour un décideur, (c) recommandations de gestion du réseau, avec limites formulées par le LLM. Chaque prompt demande de n'utiliser que les chiffres fournis.

**Second tour : ChatGPT (OpenAI).** Après ce premier tour et la lecture des résultats du projet, le groupe a rédigé sa propre interprétation de la comparaison finale (annexe B), puis a soumis le prompt (b), sans le modifier, à ChatGPT.

- **L'interprétation du groupe précède ChatGPT, pas Claude.** L'exigence du sujet (une interprétation rédigée avant de solliciter le LLM) est remplie pour le second tour ; elle ne l'est pas pour le premier, dont les réponses étaient connues du groupe au moment d'écrire.
- **Claude n'était pas neutre, et l'audit n'est pas indépendant.** Claude a aussi servi d'outil d'aide pendant la préparation du projet (code, mise en forme), et la vérification de la section 5.6 a été menée avec lui, y compris pour la réponse de ChatGPT. Chaque verdict renvoie donc à un fichier de résultats et à une valeur recalculée par `scripts/audit_reponses_llm.py` ; les principaux écarts de la réponse de ChatGPT ont d'abord été relevés par le groupe.
- **Un essai préliminaire** (9 octobre 2026, deux prompts sur le seul SARIMA, autre outil) est conservé en annexe B ; il n'entre pas dans l'analyse.

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

L'explication rend bien la distinction entre « meilleur observé » et « meilleur démontré » ; une affirmation est fausse, sur les intervalles « les mieux calibrés » (section 5.6). Elle dépasse la longueur demandée (environ 400 mots) et lisse trois points : la couverture de 95,9 % est une moyenne qui masque l'hiver, « les modèles qui tiennent compte du passé récent » ne battent pas tous la persistance de façon significative, et le coût des réseaux est sous-estimé (section 5.6).

## 5.4 Recommandations de gestion et limites

Le prompt (c) demande des recommandations à partir des prévisions du 1er au 7 septembre 2026, en invitant le LLM à formuler lui-même leurs limites. Il en propose six : (1) utiliser AR-GARCH comme référence et raisonner sur son intervalle ; (2) dimensionner la marge de sécurité sur la borne haute de l'intervalle (de 1 128,01 GWh le 1er septembre à 1 186,42 GWh le 7) et refaire la prévision chaque jour, l'erreur passant de 37,9 à 96,2 GWh/jour entre les horizons 1 et 7 ; (3) placer les opérations de maintenance le dimanche, jour de creux (de 906,98 à 938,23 GWh selon les modèles) ; (4) surveiller les jours où les modèles divergent ; (5) écarter Prophet et les méthodes naïves ; (6) garder un réseau de neurones en parallèle.

**Limites formulées par le LLM.** Le témoin fait aussi bien qu'AR-GARCH en précision ; la couverture de 95,9 % est une moyenne qui ne vaut pas forcément pour chaque saison ; un intervalle à 95 % laisse un jour sur vingt en dehors ; des modèles d'accord entre eux peuvent se tromper ensemble ; rien ne permet d'anticiper une vague de froid ; le niveau de marge acceptable dépend de la capacité disponible et du coût d'une défaillance, absents des données.

**Limites que nous ajoutons.**

- **La marge du LLM est insuffisante en hiver.** Sur le test, la couverture d'AR-GARCH tombe à 91,11 % de décembre à février (contre 97,33 % le reste de l'année), et sa RMSE y atteint 121,62 GWh/jour (contre 52,62) ; la plus forte erreur est de 329,35 GWh le 14 janvier 2026. Une marge calée sur la borne haute serait donc dépassée environ un jour sur onze en hiver, précisément quand le réseau est tendu.
- **La semaine prévue est une semaine facile.** Début septembre, les modèles s'accordent à moins de 35 GWh/jour près ; ces recommandations ne disent rien de leur comportement lors d'un épisode de froid, que la validation croisée montre environ quatre fois plus difficile à prévoir (section 4.1).
- **Le choix d'AR-GARCH n'est pas démontré.** Aucun test corrigé ne le distingue de ses concurrents ; en validation croisée, il fait jeu égal avec le GRU sans le devancer (annexe A).
- **Les données de 2026 sont consolidées**, donc révisables, et les valeurs réelles de septembre ne sont pas disponibles : aucune de ces recommandations n'a pu être confrontée à la réalité.
- **Les recommandations restent génériques** : sans capacité disponible, sans coût d'une défaillance ni prévision météo, le LLM ne peut proposer aucun seuil chiffré de marge. Elles ne constituent pas une aide à la décision d'exploitation.

## 5.5 Comparaison entre l'interprétation du groupe et la réponse de ChatGPT

Notre interprétation (environ 150 mots, sans chiffre) et la réponse de ChatGPT au prompt (b) (environ 470 mots) sont en annexe B. Le groupe avait lu tous les résultats ; ChatGPT n'a reçu que le tableau de test et les tests de Diebold–Mariano, sans rien sur la baisse d'après 2022.

- **Convergences.** Les deux textes retiennent AR-GARCH sans le dire démontré meilleur, limitent le rôle du GARCH à la mesure de l'incertitude et rappellent qu'il n'y a qu'une année de test. Cela prouve peu : ces idées se lisaient dans le prompt et dans les réponses de Claude.
- **Divergences.** *La saison* : pour le groupe, « tout se joue en hiver » ; pour ChatGPT, « la plupart des jours, la prévision est juste à environ 4 % près ». Les fichiers donnent raison au groupe : 65,4 % des jours du test sont prévus à 4 % près, mais 47,8 % en hiver, et les 90 jours d'hiver portent 61,6 % de l'erreur quadratique. *La météo* : le groupe écrit « sans prévisions météo », ChatGPT « aucun modèle n'utilise la météo », ce qui est faux. *Les réseaux* : ChatGPT juge que les modèles classiques font « au moins aussi bien », alors que la validation croisée penche pour les réseaux (section 4.1) ; le groupe ne les classe pas.
- **Ce que ChatGPT apporte et que notre texte n'a pas.** Des chiffres, la correction des comparaisons multiples et une réserve juste : « une fourchette très large couvre facilement », et le prompt ne donnait pas les largeurs (300 GWh/jour en moyenne pour AR-GARCH, 347 pour le SARIMA).
- **Simplifications, erreurs et causalités.** ChatGPT simplifie cinq fois, se trompe deux fois et généralise abusivement deux fois (tableau @tab:audit). Il n'avance aucune explication causale : c'est notre texte qui en contient.

**Limites de notre propre interprétation.**

- **Des causes non testées.** « (habitudes, prix, industrie) » est une hypothèse : la section 7.1 mesure une baisse de niveau d'environ 98 GWh/jour sans séparer ces causes. « Sans prévisions météo, les modèles se font surprendre par chaque vague de froid » est plausible, non testé et incomplet : sur les douze plus fortes erreurs d'AR-GARCH, sept sont des surestimations un jour de redoux (11,7 °C en moyenne), cinq des sous-estimations par temps froid (1,5 °C).
- **Des formules plus fortes que les résultats.** « La sensibilité au froid est restée la même » : le test ne détecte pas de changement de pente (p = 0,756), ce qui ne démontre pas l'égalité. « Ses intervalles sont les plus fiables » : AR-GARCH est le seul à atteindre 95 % et tient le mieux en hiver (91,1 % contre 86,7 % pour le SARIMA), mais le SARIMA est plus proche de 95 % sur l'ensemble du test ; les deux LLM font la même erreur.
- **Une portée surestimée.** Quand ce texte a été écrit, les plis de validation croisée ne portaient pas encore sur AR-GARCH, et il ne cite aucun chiffre.

## 5.6 Audit des affirmations des LLM

Nous avons relevé 52 affirmations chiffrées ou causales, 32 dans les trois réponses de Claude (dont 10 pour le prompt b) et 20 dans celle de ChatGPT, et confronté chacune à un fichier du projet (audit complet en annexe B).

[[TAB:audit_bilan|Bilan de l'audit par outil|Les deux outils commettent les deux mêmes erreurs ; ChatGPT ajoute deux généralisations abusives.]]

| LLM | Affirmations | Correctes | Simplifiées | Fausses | Généralisations abusives | Causalités non fondées |
|---|---|---|---|---|---|---|
| Claude, prompts (a), (b) et (c) | 32 | 20 | 10 | 2 | 0 | 0 |
| ChatGPT, prompt (b) | 20 | 11 | 5 | 2 | 2 | 0 |

Sur les nombres cités, 156 des 170 de Claude et 25 des 28 de ChatGPT figurent dans le prompt ; les autres sont des seuils, des ordres de modèle, des arrondis ou des calculs exacts. **Deux erreurs de Claude avaient échappé au premier audit**, qui portait sur 29 affirmations et n'en jugeait aucune fausse : elles sont apparues en appliquant à ses réponses les contrôles faits pour ChatGPT.

[[TAB:audit|Affirmations fausses, généralisées ou simplifiées les plus importantes|Aucune de ces erreurs ne porte sur un chiffre inventé.]]

| LLM (prompt) | Affirmation | Verdict | Correction |
|---|---|---|---|
| ChatGPT (b), Claude (b) | Couverture d'AR-GARCH « la plus proche » de 95 %, intervalles « les mieux calibrés » | fausse | SARIMA : 94,36 %, à 0,64 point de 95 % ; AR-GARCH : 95,90 %, à 0,90 point |
| ChatGPT (b), Claude (c) | « Aucun modèle n'utilise la météo » | fausse | Le prompt disait « aucune prévision météo » ; le VAR et le VECM utilisent la température observée |
| ChatGPT (b) | Les modèles classiques font « au moins aussi bien » que les réseaux | généralisation abusive | Vrai pour AR-GARCH seul : VAR, SARIMA et VECM (78,96 à 87,56) sont derrière le LSTM (75,07) et le GRU (76,40) |
| ChatGPT (b) | Ils « battent nettement » les règles naïves et Prophet | généralisation abusive | 4 comparaisons sur 12 significatives après Holm en perte quadratique, aucune contre le naïf saisonnier |
| ChatGPT (b), Claude (b) | Temps de calcul faibles (« moins de 16 secondes ») | simplifiée | Vrai par ajustement ; 38,7 s (LSTM), 75,9 s (GRU) et 99,6 s (Prophet) pour le protocole |
| ChatGPT (b) | RMSE d'environ 5,9 % de la consommation moyenne ; « un jour ordinaire, l'écart typique est de 49 GWh » | simplifiée | 6,15 % de la moyenne du test (le prompt imposait celle de l'apprentissage) ; 49 GWh est la MAE, l'erreur médiane est de 29,88 GWh/jour |

**Lecture critique.** Aucun chiffre n'est inventé : les erreurs viennent de la lecture des chiffres du prompt (comparer deux écarts à 95 %, reprendre « prévision météo » en « météo », étendre à une famille de modèles un résultat donné pour un seul). Les deux bilans ne se comparent pas terme à terme : trois prompts contre un, une seule réponse par outil, un découpage plus fin pour ChatGPT.

## 5.7 Apport et limites des LLM

**Ce qu'ils ont apporté.** Un cadrage rapide (familles de modèles à tester et diagnostics à faire, qui recoupent la démarche du projet), une vulgarisation claire de notions difficiles (erreur quadratique, intervalle à 95 %, différence non significative) et des limites justes, formulées spontanément. Nous n'avons pas mesuré le temps gagné.

**Ce qu'ils n'ont pas su faire.** Trouver le modèle retenu, qui exigeait l'ACF, la PACF et une validation. Voir ce que les chiffres transmis ne contenaient pas : saisonnalité annuelle dominante, ruptures de 2020 et 2022, dégradation des intervalles en hiver. Chiffrer une marge de sécurité. Vérifier leurs propres affirmations.

**Ce que montre la comparaison des deux outils.** Sur le même prompt, ChatGPT respecte mieux la longueur demandée (environ 470 mots contre 580) et formule une réserve que Claude n'a pas, mais il généralise davantage. Les deux commettent la même erreur sur la couverture : l'accord de deux LLM ne vaut pas vérification. Le second outil a surtout servi de révélateur : c'est en auditant ChatGPT que nous avons retrouvé deux erreurs de Claude, manquées par un audit mené avec Claude lui-même. Écrire notre interprétation avant de lire ChatGPT nous a montré ce qu'il ne pouvait pas voir (l'hiver), et sa réponse chiffrée a fait ressortir nos affirmations non testées. Aucun des deux ne remplace les calculs, les diagnostics ni la relecture critique de chaque chiffre.
