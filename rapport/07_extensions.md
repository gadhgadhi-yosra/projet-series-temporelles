# 7 — Extensions

Les extensions du sujet sont traitées de trois manières : des **variables exogènes** (jour férié, jour de la semaine et harmoniques annuelles pour le VAR, le VECM, l'AR-GARCH, Prophet et les réseaux ; température comme variable endogène du VAR ; degrés-jours `hdd` et `cdd` dans les contrefactuels), l'**étude de la corrélation dynamique** entre température et consommation (7.1) et l'**analyse contrefactuelle** des effets du premier confinement et de la sobriété (7.2). Nous n'avons pas appliqué de détection d'événements par embeddings de texte.

## 7.1 Corrélation glissante entre température et consommation

Cette extension, implémentée en R (`06_section3_R.ipynb`), étudie si le lien température–consommation est stable ou change selon la saison et au fil des années.

[[FIG:correlation_glissante|../figures/R/correlation_glissante_R.png|Corrélation glissante entre température et consommation (30, 90 et 365 jours)|Le lien est négatif de l'automne au printemps (on chauffe) et devient positif chaque fin d'été (on climatise) ; sur 365 jours il reste fort, avec deux affaiblissements en 2020 et en 2026.]]

- **Le lien dépend de la saison.** Sur 90 jours, la corrélation reste autour de −0,90 d'octobre à juin et devient positive chaque fin d'été, jusqu'à +0,69. C'est la courbe en U de la section 2.6 vue dans le temps. Sur 30 jours, les bascules sont plus brutales (de −0,98 à +0,97) : la fenêtre est courte et sensible à une seule vague de chaleur ou de froid.
- **Sur 365 jours**, le lien reste fort (de −0,93 à −0,77), avec deux affaiblissements : 2020 (le confinement réduit la consommation sans lien avec la météo) et 2026 (l'été 2026 est le plus chaud de la série : 260 degrés-jours de climatisation de juin à août, contre 137 au précédent maximum, en 2022).
- **Le lien n'est pas une coïncidence de calendrier** : une fois l'effet du calendrier retiré (jusqu'à −301 GWh/jour pour un dimanche férié par rapport à un mardi), la corrélation sur toute la période passe de −0,83 à −0,86 ; elle garde la même forme saisonnière sur les variations journalières (annexe A, tableau @tab:annexe_profil).
- **D'un hiver à l'autre**, la corrélation d'hiver est stable (de −0,88 à −0,95), sauf en 2019-2020 (−0,68), qui inclut le début du confinement, et la pente reste comprise entre −40,2 et −56,5 GWh/jour par °C sans tendance (annexe A, tableau @tab:annexe_hivers). En revanche, la consommation estimée à 8 °C passe de 1 513–1 575 GWh/jour (hivers 2016-17 à 2019-20) à 1 424–1 469 GWh/jour depuis l'hiver 2022-23.

[[TAB:rupture|Effet de la sobriété sur la sensibilité au froid|À température égale, la consommation d'hiver a baissé d'environ 98 GWh/jour depuis octobre 2022, sans changement significatif de pente (p = 0,756).]]

| Terme de la régression d'hiver | Estimation (GWh/jour) | Écart-type | p-value |
|---|---|---|---|
| Constante | 1 929,55 | 16,22 | < 0,001 |
| Température (pente avant octobre 2022, par °C) | −48,42 | 1,69 | < 0,001 |
| Après octobre 2022 (décalage de niveau) | −98,42 | 22,78 | < 0,001 |
| Température × après (changement de pente, par °C) | +0,71 | 2,30 | 0,756 |

La courbe consommation–température s'est donc **décalée vers le bas sans changer de pente** : la sobriété a surtout abaissé la consommation de base (intervalle à 95 % de la baisse : environ 54 à 143 GWh/jour). La régression attribue à la sobriété toute baisse survenue après octobre 2022 : le prix de l'énergie et le ralentissement industriel ne sont pas séparés.

## 7.2 Contrefactuels : premier confinement et sobriété

Cette analyse (`03_contrefactuels.ipynb`) répond à la question : combien d'électricité la France n'a-t-elle pas consommée à cause du premier confinement de 2020 et de la crise énergétique ? Le principe est celui de la méthode de l'INSEE : apprendre la relation « normale » entre consommation, météo et calendrier sur une période sans choc, prédire ce qu'aurait été la consommation pendant le choc, puis mesurer l'écart **réel − contrefactuel** (un écart négatif signifie que la France a consommé moins que prévu).

### Modèle de référence et validation

Le modèle est une régression linéaire (moindres carrés) de la consommation journalière sur 20 variables explicatives et une constante : degrés-jours de chauffage `hdd`, `hdd` lissé sur 3 jours (inertie thermique des bâtiments), `cdd` ; jour de la semaine (6 indicatrices), jour férié, période de Noël et 1–20 août ; quatre paires de termes de Fourier annuels. Aucune tendance n'est ajoutée : elle dégrade la validation (extrapolation risquée). Ce modèle est **indépendant des modèles de prévision** ; pour ne pas toucher à la période de test, l'analyse de la sobriété s'arrête à l'hiver 2024-25.

[[TAB:cf_validation|Validation du modèle contrefactuel en période sans choc|Le modèle prédit une année inconnue avec une erreur de 2,6 %, mais il « détecte » à tort un écart d'environ −1,1 % sur un hiver sans choc : c'est son biais.]]

| Test | Erreur moyenne (MAPE) | Biais | R² d'apprentissage |
|---|---|---|---|
| 2019 (appris sur 2016-2018) | 2,58 % | −1,20 % | 0,978 |
| Placebo : hiver 2018-19 (appris jusqu'en septembre 2018) | 2,49 % | −1,09 % | 0,979 |

Ce **biais en période normale**, que nous attribuons à un léger recul tendanciel de la consommation, signifie qu'un écart n'est attribuable à un choc que s'il dépasse nettement 1 à 1,5 %, et que les effets estimés peuvent être **surestimés d'environ 1 point**.

### Résultats

[[TAB:cf_covid|Effet du premier confinement|Le premier confinement a réduit la consommation d'environ 8,06 TWh (−12,2 %) ; sur la fenêtre de l'INSEE, −13,48 % contre −14 % publié.]]

| Fenêtre | Réel (TWh) | Contrefactuel (TWh) | Écart (TWh) | Écart (%) |
|---|---|---|---|---|
| Confinement complet, 17 mars – 10 mai 2020 | 58,04 | 66,10 | −8,06 | −12,20 |
| Fenêtre INSEE, 23 mars – 26 avril 2020 | 37,44 | 43,27 | −5,83 | −13,48 |

Le modèle est appris du 1er janvier 2016 au 29 février 2020, avant toute mesure sanitaire. L'effet est maximal fin mars puis s'atténue : la consommation résidentielle augmente (télétravail) et l'activité reprend. En retirant le biais du modèle, l'effet propre du confinement est d'environ −11 %. La valeur de −14 % de l'INSEE (note de conjoncture de mai 2020) est citée dans le notebook et n'a pas été revérifiée pour ce rapport.

[[FIG:cf_covid|../figures/contrefactuel_covid.png|Contrefactuel du premier confinement|La consommation observée passe sous le contrefactuel dès la mi-mars 2020, avec un écart maximal fin mars, puis l'écart se résorbe.]]

[[TAB:cf_sobriete|Effet de la crise énergétique et de la sobriété|La baisse est de 8,27 % en 2022-23 et ne disparaît pas ensuite (7,19 % puis 6,57 %), ce qui suggère une part structurelle.]]

| Hiver | Réel (TWh) | Contrefactuel (TWh) | Écart (TWh) | Écart (%) |
|---|---|---|---|---|
| 2022-23 | 243,54 | 265,49 | −21,96 | −8,27 |
| 2023-24 | 244,42 | 263,36 | −18,95 | −7,19 |
| 2024-25 | 252,26 | 269,99 | −17,74 | −6,57 |

Le modèle est appris sur 2016-2019 uniquement (comportement d'avant les crises, COVID exclu). À météo et calendrier égaux, la consommation de l'hiver 2022-23 est inférieure de 8,27 % (environ 22 TWh) à celle qu'aurait produite le comportement de 2016-2019 ; le notebook cite une estimation de RTE d'« environ 9 % » par rapport à 2014-2019 (non revérifiée ici), cohérente malgré des périodes de référence proches mais non identiques. Le décrochage commence en septembre-octobre 2022 et culmine en novembre 2022 (−10,4 % d'après le notebook). **La baisse ne disparaît pas** (−7,19 % en 2023-24, −6,57 % en 2024-25) : une partie de la sobriété semble devenue structurelle (habitudes, équipements, industrie électro-intensive), hypothèse que ce modèle ne permet pas de démontrer. La régression d'hiver du tableau @tab:rupture, obtenue par une autre méthode, va dans le même sens. Avant la crise (2021-22), les écarts restent entre 0 et −4 %, ce qui borne l'incertitude de la mesure.

[[FIG:cf_sobriete|../figures/contrefactuel_sobriete.png|Écart mensuel entre consommation réelle et contrefactuel|La consommation est inférieure au contrefactuel à partir de l'automne 2022, de façon durable, avec un creux de −10,4 % en novembre 2022.]]

### Limites

Le biais d'environ −1 % pourrait surestimer les effets. Les résidus de la régression sont autocorrélés : les intervalles de prévision à 95 % sont probablement trop étroits. La température nationale n'est pas pondérée par la population. Le contrefactuel attribue au choc tout ce que le modèle n'explique pas (prix de l'électricité, activité économique, évolution du parc : pompes à chaleur, véhicules électriques). Les références officielles (INSEE, RTE) sont reprises du notebook.
