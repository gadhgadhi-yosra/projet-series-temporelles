# Introduction

## Thématique et question de modélisation

Nous avons choisi la thématique **environnementale et énergétique** et, dans celle-ci, la **consommation électrique quotidienne de la France** : cette série concentre une saisonnalité annuelle et hebdomadaire très marquée, une forte dépendance à la température, et deux ruptures liées à des événements publics (le premier confinement de 2020 et la crise énergétique de 2022 avec son plan de sobriété), ce qui permet de tester à la fois des modèles de prévision et une analyse contrefactuelle.

Nous poursuivons deux objectifs :

1. **Prévoir** la consommation à sept jours et comparer rigoureusement dix modèles : SARIMA, VAR, VECM, AR-GARCH, Prophet, LSTM, GRU, un hybride SARIMA + LSTM et deux références naïves (dernière valeur et semaine précédente).
2. **Mesurer des effets** : combien d'électricité la France n'a-t-elle *pas* consommée à cause du premier confinement et de la sobriété ? La méthode estime ce que la consommation aurait été sans le choc, à météo et calendrier identiques, puis mesure l'écart avec la consommation observée.

## Série retenue

La série cible est la consommation électrique quotidienne `conso_gwh`, en GWh/jour, du 1er janvier 2016 au 31 août 2026, soit **3 896 jours consécutifs** sans valeur manquante. Elle est accompagnée de la température moyenne nationale, de degrés-jours de chauffage et de climatisation, du jour de la semaine et des jours fériés (section 1). Les sources sont RTE (éCO2mix) pour la consommation et ODRÉ pour la température ; les transformations appliquées par les fournisseurs et par nous sont décrites en section 1.

## Découpage chronologique 90 % / 10 %

Le découpage est chronologique, jamais aléatoire, et commun à tous les modèles :

[[TAB:decoupage|Découpage chronologique commun|Le test représente 10 % de la série (390 jours) et ne sert à aucun choix de modèle.]]

| Période | Dates | Jours |
|---|---|---|
| Apprentissage (90 %) | 1er janvier 2016 → 6 août 2025 | 3 506 |
| dont estimation interne | jusqu'au 11 juin 2025 | 3 450 |
| dont validation interne | 12 juin → 6 août 2025 | 56 |
| Test externe (10 %) | 7 août 2025 → 31 août 2026 | 390 |

Les modèles de prévision produisent des prévisions à un horizon de 1 à 7 jours, **par blocs de 7 jours** : les observations d'un bloc ne servent qu'à partir du bloc suivant. Le test comprend 55 blocs complets et un dernier bloc de 5 jours. Les prévisions finales portent sur le **1er–7 septembre 2026**, car la dernière observation est celle du 31 août 2026. Le modèle contrefactuel (section 7.2) est indépendant des modèles de prévision et n'utilise aucune donnée du test.

## Résultat principal

Sur le test (390 jours), AR-GARCH(1,2)-t a la plus petite erreur (RMSE 74,45 GWh/jour), mais aucun test de Diebold–Mariano corrigé (Holm) ne le distingue de SARIMA, LSTM, GRU, VAR(3) ni de l'hybride. SARIMA(2,1,1)(0,1,1)[7] est le modèle retenu par la règle de validation interne ; AR-GARCH est le meilleur observé sur le test, à égalité avec le GRU en validation croisée ; nous ne concluons pas à une supériorité durable. Le témoin « AR à variance constante » (RMSE 74,06 GWh/jour) fait aussi bien : la moyenne autorégressive avec calendrier explique l'essentiel du gain.

## Organisation du rapport et auteurs

[[TAB:auteurs|Plan du rapport et auteurs de chaque partie|Chaque partie est portée par un membre du groupe ; les sections 8 et 9 sont communes.]]

| Section | Contenu | Auteur(e) |
|---|---|---|
| 1 | Données : source, période, transformations | Fayfa |
| 2 | Analyse exploratoire | Fayfa |
| 3.1 | ARIMA et SARIMA | Yosra |
| 3.2 | VAR, causalité de Granger, cointégration, VECM | Ghada |
| 3.3 | ARCH et GARCH | Ghada |
| 3.4 | Réplication en R et comparaison avec Python | Anwar |
| 4.1 | LSTM et GRU, validation croisée temporelle | Anas |
| 4.2 | Hybride SARIMA + LSTM | Anas |
| 4.3 | Prophet | Ghada |
| 5 | IA générative et LLM | Yosra |
| 6 | Prévision et évaluation comparative | Anas |
| 7 | Extensions : corrélation glissante et contrefactuels | Anwar (7.1), Fayfa (7.2) |
| 8 | Discussion critique | groupe |
| 9 | Conclusion | groupe |

Le code est fourni dans huit notebooks : sept en Python (préparation, analyse exploratoire, contrefactuels, visualisations, SARIMA, VAR/VECM/GARCH/Prophet, réseaux de neurones) et un en R (socle classique de la section 3 et extension 7.1). Le socle classique (section 3) est donc implémenté en R **et** en Python ; le socle avancé (section 4) et les extensions sont en Python, sauf l'extension 7.1, en R.
