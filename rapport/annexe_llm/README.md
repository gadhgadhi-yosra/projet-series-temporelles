# Annexe LLM — prompts, réponses et interprétation du groupe

Ce dossier contient les prompts, les réponses intégrales et l'interprétation du groupe utilisés en section 5 du rapport. Les réponses ne sont ni résumées ni corrigées : leurs limites sont consignées dans les fichiers d'audit.

## Premier tour (Claude)

LLM consulté : Claude (Anthropic), modèle Claude Opus 5.5 (identifiant `claude-opus-5-5`), le 11 octobre 2026.

| Fichier | Contenu |
|---|---|
| `03_prompt_a_hypotheses_modeles.txt`, `03_reponse_integrale.md` | prompt (a) et réponse intégrale : hypothèses de modèles à partir des statistiques descriptives |
| `04_prompt_b_vulgarisation_decideur.txt`, `04_reponse_integrale.md` | prompt (b) et réponse intégrale : vulgarisation de la comparaison finale pour un décideur |
| `05_prompt_c_recommandations_gestion.txt`, `05_reponse_integrale.md` | prompt (c) et réponse intégrale : recommandations de gestion du réseau, limites formulées par le LLM |

## Interprétation du groupe et second tour (ChatGPT)

| Fichier | Contenu |
|---|---|
| `interpretation_personnelle.md` | interprétation du groupe, rédigée après le premier tour et la lecture des résultats du projet, avant la consultation de ChatGPT ; seules l'orthographe et la typographie ont été corrigées |
| `06_reponse_chatgpt.md` | réponse intégrale de ChatGPT (OpenAI) au prompt (b), soumis sans modification |

## Audit

| Fichier | Contenu |
|---|---|
| `audit_gabarit.csv` | audit des 52 affirmations chiffrées ou causales (32 de Claude, 20 de ChatGPT) : affirmation, fichier de vérification, verdict, correction |

Les prompts sont générés par `scripts/preparer_prompts_llm.py` à partir des fichiers de `exports/`. Les vérifications chiffrées de l'audit sont produites par `scripts/audit_reponses_llm.py` (`exports/audit_llm_nombres.csv`, `exports/audit_llm_verifications.csv`). Claude a aussi servi d'outil d'aide pendant la préparation du projet ; l'audit, mené avec le même outil y compris pour la réponse de ChatGPT, n'est pas un contrôle indépendant.

## Essai préliminaire (modèle SARIMA seul, 9 octobre 2026)

| Fichier | Contenu |
|---|---|
| `contexte_resultats.json` | résultats calculés transmis au LLM |
| `01_prompt_vulgarisation.txt`, `01_reponse_integrale.md` | prompt et réponse intégrale : vulgarisation |
| `02_prompt_recommandations.txt`, `02_reponse_integrale.md` | prompt et réponse intégrale : recommandations |
| `audit_affirmations.csv` | contrôle des affirmations des deux réponses |
| `manifest.json` | outil utilisé, provenance et empreintes des fichiers de l'essai préliminaire |

Cet essai est conservé pour mémoire ; il n'entre pas dans l'analyse de la section 5.
