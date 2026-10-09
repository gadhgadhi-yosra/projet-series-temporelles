# Prévisions à intégrer — WattIf

Modèle : SARIMA(2, 1, 1)(0, 1, 1)[7].

- Cible : consommation électrique quotidienne `conso_gwh`.
- Unité : **GWh/jour** pour toutes les colonnes numériques du CSV de prévisions.
- Dernière observation : **31 août 2026**.
- Dates prévues : **1er–7 septembre 2026** (ne pas les remplacer par des dates d'octobre).
- CSV UTF-8, séparateur virgule, point décimal, dates ISO `YYYY-MM-DD`, sans index.
- Colonnes : `date`, `prevision`, `borne_inferieure_95`, `borne_superieure_95`.
- Bornes : intervalles de prévision gaussiens nominaux à 95 %, conditionnels au modèle. Leur couverture future n'est pas garantie.

Les diagnostics résiduels restent défavorables ; cette limite doit accompagner la présentation. Les données réelles de septembre ne sont pas présentes dans le CSV source. Les prévisions ne constituent pas une comparaison déjà observée avec ces valeurs réelles.

`scores_test.csv` décrit le test historique du 7 août 2025 au 31 août 2026, en blocs successifs de sept jours (dernier bloc de cinq), avec paramètres fixes et états actualisés. Le modèle n'a pas été sélectionné à partir des erreurs de ce test. Les métadonnées contiennent les ordres, le protocole et l'empreinte des données.

Ce dossier est prêt à transmettre manuellement. Aucun envoi automatique n'a été effectué.
