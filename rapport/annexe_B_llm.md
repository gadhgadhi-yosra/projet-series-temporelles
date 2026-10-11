# Annexe B — Échanges avec les LLM

Cette annexe regroupe les prompts, les réponses intégrales et l'interprétation du groupe (section 5). Les réponses ne sont ni résumées ni corrigées ; leurs limites sont traitées dans l'audit (B.4). **LLM consultés : Claude (Anthropic), modèle Claude Opus 5.5 (identifiant `claude-opus-5-5`), le 11 octobre 2026, pour les prompts (a), (b) et (c) ; ChatGPT (OpenAI) pour le prompt (b).** Les prompts sont générés par `scripts/preparer_prompts_llm.py` à partir des fichiers de résultats ; les fichiers d'origine sont dans `rapport/annexe_llm/`.

## B.1 Essai préliminaire

Deux prompts, portant uniquement sur le modèle SARIMA de la section 3.1, ont été soumis le 9 octobre 2026 à un autre outil (identifié dans `manifest.json`). Ils n'entrent pas dans l'analyse de la section 5 ; les fichiers sont conservés tels quels.

[[TAB:tour1|Fichiers de l'essai préliminaire|L'essai préliminaire est conservé pour mémoire et n'entre pas dans l'analyse de la section 5.]]

| Objet | Prompt | Réponse intégrale |
|---|---|---|
| Vulgarisation du SARIMA | `01_prompt_vulgarisation.txt` | `01_reponse_integrale.md` |
| Recommandations à partir des prévisions du SARIMA | `02_prompt_recommandations.txt` | `02_reponse_integrale.md` |
| Audit des affirmations des deux réponses | `audit_affirmations.csv` | |

## B.2 Premier tour (Claude) : prompts et réponses intégrales

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

## B.3 Interprétation du groupe et second tour (ChatGPT)

### Interprétation du groupe

Ce texte (`interpretation_personnelle.md`) a été rédigé par le groupe après le premier tour et la lecture des résultats du projet, avant la consultation de ChatGPT. Seules l'orthographe et la typographie ont été corrigées.

[[INSERER_LIGNES:rapport/annexe_llm/interpretation_personnelle.md]]

### Réponse intégrale de ChatGPT au prompt (b)

Le prompt (b) reproduit en B.2 a été soumis à ChatGPT sans modification. Sa réponse (`06_reponse_chatgpt.md`) est reproduite telle quelle.

[[INSERER_LIGNES:rapport/annexe_llm/06_reponse_chatgpt.md]]

## B.4 Audit complet des affirmations des LLM

[[TAB:audit_complet|Audit des 52 affirmations chiffrées ou causales : 32 dans les trois réponses de Claude, 20 dans celle de ChatGPT|Trente et une affirmations sont correctes, quinze simplifiées, quatre fausses et deux sont des généralisations abusives ; aucune causalité n'est présentée comme démontrée.]]

[[TABLE_CSV:rapport/annexe_llm/audit_gabarit.csv]]
