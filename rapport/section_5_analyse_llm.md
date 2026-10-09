# 5 — Analyse assistée par LLM, recommandations et contrôle critique

Cette section a été préparée avec assistance IA le 9 octobre 2026. Elle distingue les résultats calculés des interprétations et des pistes non testées.

## 5.1 Démarche réellement suivie et écart au protocole initial

Le protocole demandé prévoyait une interprétation personnelle avant toute consultation d'un LLM. L'étudiante a confirmé ne pas avoir rédigé ce texte avant les explications déjà fournies par l'assistant. Cette condition n'a donc **pas été satisfaite** ; aucun texte n'a été reconstitué ou attribué à l'étudiante pour donner l'apparence du contraire.

Les modèles et les tests ont été calculés en Python. Un bilan statistique assisté a ensuite été rédigé dans la section 3.1. Deux prompts de restitution ont été formulés pour obtenir une vulgarisation puis des recommandations. Les réponses ont été produites par l'assistant de la même conversation et conservées intégralement dans l'annexe. Ce n'est pas une expérience avec un évaluateur indépendant, ni une comparaison de plusieurs fournisseurs de LLM.

La comparaison possible porte donc sur **le bilan statistique calculé et assisté, puis la restitution du LLM**, et non sur une analyse humaine indépendante antérieure. Une réflexion personnelle après assistance est prévue dans `reflexion_personnelle_a_rediger.md` ; seule l'étudiante peut en rédiger le contenu.

## 5.2 Résultats soumis au LLM

Les éléments transmis comprennent les paramètres du modèle sélectionné, le tableau de comparaison interne, les métriques externes, les diagnostics, les prévisions avec leurs bornes, les unités et les limites méthodologiques. Le contenu exact est archivé dans les prompts, et les données structurées sont dans `annexe_llm/contexte_resultats.json`.

Le modèle SARIMA(2,1,1)(0,1,1)[7] obtient une RMSE interne de 42,67 GWh/jour. Après fixation des ordres, le test externe donne une MAE de 53,12 et une RMSE de 82,38 GWh/jour. Le naïf saisonnier donne une RMSE de 113,93, soit un gain relatif de RMSE de 27,69 % pour le modèle retenu. La couverture agrégée des intervalles nominaux à 95 % est de 94,36 %. Les diagnostics finaux restent défavorables à l'absence d'autocorrélation, à la normalité et à l'absence d'effet ARCH.

## 5.3 Apport de la vulgarisation

La première réponse explique les composantes de SARIMA, distingue MAE et RMSE, et sépare la sélection du modèle de la validité de ses hypothèses. Elle traduit les métriques en termes accessibles sans les transformer en économies d'énergie ou en probabilités de réussite de chaque prévision. Elle précise aussi que les prévisions finales correspondent au 1er–7 septembre 2026, après la dernière observation, et non à la semaine suivant la rédaction du rapport.

La seconde réponse propose de conserver les références naïves, de présenter les diagnostics défavorables et de joindre les métadonnées à la livraison. Elle cite des améliorations possibles — calendrier, termes annuels, météo réellement disponible à la date de prévision, intervalles mieux adaptés — tout en indiquant qu'elles n'ont pas été évaluées dans ce travail.

## 5.4 Comparaison critique et recherche d'hallucinations

| Point vérifié | Bilan statistique / preuve | Restitution LLM | Verdict |
|---|---|---|---|
| Modèle retenu | `selection_avant_test.json` : (2,1,1)(0,1,1)[7] | Même spécification | Conforme |
| RMSE de test | `scores_test.csv` : 82,382 contre 113,927 pour le naïf saisonnier | 82,38 et 113,93, gain de 27,69 % | Conforme aux arrondis |
| Performance auto_arima | `comparaison_validation_complete.csv` : comparaison interne uniquement | La réponse situe la comparaison sur la validation | Conforme ; ne pas extrapoler au test des modèles auto |
| Intervalles | Couverture observée 0,94359 ; largeur moyenne 346,749 | 94,36 % et 346,75 GWh/jour, sans garantie future | Conforme |
| Diagnostics | P-values faibles dans `diagnostics_modele_retenu.csv` | Les trois limites sont mentionnées | Conforme ; le modèle n'est pas déclaré parfait |
| Dates prédites | `previsions_7j.csv` : 1er–7 septembre 2026 | Mêmes dates | Conforme |
| Causalité | Aucun modèle causal ni exogène dans cette partie | Aucune cause économique présentée comme démontrée | Pas de causalité inventée repérée |
| Analyse personnelle antérieure | Absente, confirmé par l'étudiante | Absence déclarée | Conforme ; exigence initiale non satisfaite |
| Améliorations proposées | Aucun résultat expérimental pour calendrier/météo/autres intervalles | Pistes explicitement non testées | Recommandations, pas résultats validés |

Aucune hallucination factuelle n'a été identifiée parmi ces affirmations vérifiées dans les deux réponses archivées. Cela ne prouve pas l'absence de toute erreur. Le contrôle a été effectué dans la même session par l'assistant et doit être relu par l'étudiante. Le tableau détaillé des citations courtes et des fichiers de preuve est archivé dans `annexe_llm/audit_affirmations.csv`.

Plusieurs formulations auraient constitué des erreurs, mais **ne sont pas des hallucinations observées dans ces réponses** : « les résidus sont du bruit blanc », « la normalité est validée », « l'intervalle garantit 95 % pour chaque jour », « SARIMA réduit la consommation de 27,69 % », ou « l'étudiante avait écrit son analyse avant le LLM ». Les distinguer des erreurs réellement présentes évite de fabriquer artificiellement des hallucinations pour remplir l'annexe.

## 5.5 Recommandations et limites

Pour ce projet, le modèle retenu fournit une référence de prévision utile sur le test étudié, avec ses bornes et ses limites. Les diagnostics suggèrent de ne pas présenter les intervalles gaussiens comme une certitude. La couverture moyenne proche de 95 % peut masquer des différences entre saisons ou horizons ; les erreurs par horizon sont fournies séparément.

La validation initiale est estivale, a été réutilisée pendant le développement et était déjà incluse dans l'EDA de Fayfa. Le test externe est distinct pour la sélection de cette partie, mais une seule période historique ne garantit pas la robustesse future. Les effets calendaires, météorologiques et annuels ne sont pas explicitement modélisés. Les propositions d'extension devraient être évaluées sur un nouveau protocole, sans choisir de nouveaux paramètres en exploitant les erreurs du test final déjà consulté.

Le LLM facilite l'explication et la structuration, mais il ne remplace ni les calculs, ni le contrôle des fichiers, ni le travail personnel demandé. Le CSV peut être transmis à Anas pour l'intégration du projet ; aucune décision réelle d'exploitation du réseau n'est justifiée par ces seuls résultats.
