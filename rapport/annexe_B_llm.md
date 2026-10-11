# Annexe B — Échanges avec le LLM

Cette annexe regroupe les prompts et les réponses intégrales de la section 5. Les réponses ne sont ni résumées ni corrigées ; leurs limites sont traitées dans l'audit (B.3). **LLM consulté : Claude (Anthropic), modèle Claude Opus 5.5 (identifiant `claude-opus-5-5`), le 11 octobre 2026.** Les prompts sont générés par `scripts/preparer_prompts_llm.py` à partir des fichiers de résultats ; les fichiers d'origine sont dans `rapport/annexe_llm/`.

## B.1 Premier tour (exploratoire)

Deux prompts, portant uniquement sur le modèle SARIMA de la section 3.1, ont été soumis le 9 octobre 2026 à un autre outil (identifié dans `manifest.json`). Ils n'entrent pas dans l'analyse de la section 5 ; les fichiers sont conservés tels quels.

[[TAB:tour1|Fichiers du premier tour|Le premier tour est conservé pour mémoire et n'entre pas dans l'analyse de la section 5.]]

| Objet | Prompt | Réponse intégrale |
|---|---|---|
| Vulgarisation du SARIMA | `01_prompt_vulgarisation.txt` | `01_reponse_integrale.md` |
| Recommandations à partir des prévisions du SARIMA | `02_prompt_recommandations.txt` | `02_reponse_integrale.md` |
| Audit des affirmations des deux réponses | `audit_affirmations.csv` | |

## B.2 Second tour : prompts et réponses intégrales

### Prompt (a) : hypothèses de modèles à partir des statistiques descriptives

[[INCLURE:rapport/annexe_llm/03_prompt_a_hypotheses_modeles.txt]]

**Réponse intégrale de Claude au prompt (a)** (`03_reponse_integrale.md`) :

[[INSERER:rapport/annexe_llm/03_reponse_integrale.md]]

### Prompt (b) : explication vulgarisée pour un décideur

[[INCLURE:rapport/annexe_llm/04_prompt_b_vulgarisation_decideur.txt]]

**Réponse intégrale de Claude au prompt (b)** (`04_reponse_integrale.md`) :

[[INSERER:rapport/annexe_llm/04_reponse_integrale.md]]

### Prompt (c) : recommandations de gestion du réseau avec limites

[[INCLURE:rapport/annexe_llm/05_prompt_c_recommandations_gestion.txt]]

**Réponse intégrale de Claude au prompt (c)** (`05_reponse_integrale.md`) :

[[INSERER:rapport/annexe_llm/05_reponse_integrale.md]]

## B.3 Audit complet des affirmations du LLM

[[TAB:audit_complet|Audit des 29 affirmations chiffrées ou causales des trois réponses|Vingt affirmations sont correctes et neuf simplifiées ; aucune n'est fausse et aucune causalité n'est présentée comme démontrée.]]

[[TABLE_CSV:rapport/annexe_llm/audit_gabarit.csv]]
