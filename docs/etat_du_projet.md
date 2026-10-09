# État des tâches — 9 octobre 2026

| Tâche | État et livrable |
|---|---|
| Analyser ACF/PACF | Réalisé, avec prudence sur la différenciation ; notebook et section 3.1 |
| Construire ARIMA/SARIMA | Réalisé : 11 candidats manuels, dont 4 ajoutés après diagnostics |
| Comparer avec auto_arima | Réalisé : auto_ARIMA et auto_SARIMA sur la même validation interne |
| Ljung–Box, Jarque–Bera, ARCH-LM | Réalisé sur les candidats et le modèle retenu ; limites résiduelles conservées |
| Sélection et test externe | Réalisé : choix figé avant test, comparaison aux deux références naïves |
| Prévisions 7 jours avec intervalles | Réalisé : 1er–7 septembre 2026, intervalles nominaux à 95 % |
| Export pour Anas | Réalisé : dossier et ZIP `livraison_anas`, sans envoi |
| Analyse personnelle avant LLM | Non satisfaite : absence confirmée par l'étudiante ; impossible à reconstituer rétroactivement |
| Prompts et réponses LLM intégrales | Réalisé dans `rapport/annexe_llm`, même assistant et même session, sans faux appel externe |
| Vulgarisation, recommandations et limites | Réalisé, sections du rapport et annexe |
| Comparaison personnelle / LLM | La comparaison humaine préalable n'est pas disponible ; contrôle factuel données/LLM fourni et limite déclarée |
| Audit des hallucinations | Réalisé sur les affirmations archivées ; aucune hallucination factuelle repérée dans celles vérifiées, audit non indépendant |
| Sections 3.1 et 5 | Rédigées avec assistance IA, à relire et à intégrer au rapport de groupe |
| Réflexion personnelle postérieure | À rédiger par l'étudiante, dans le support prévu |

Le modèle retenu est SARIMA(2,1,1)(0,1,1)[7]. La finalisation du livrable ne signifie pas que toutes les hypothèses du modèle sont vérifiées. Le rapport conserve les diagnostics défavorables et les limites de validation.

Les quatre notebooks de Fayfa, ses figures et son CSV sont préservés (empreintes dans `import_fayfa.json`). Les documents de première comparaison décrivent une étape historique, avant les quatre candidats complémentaires.
