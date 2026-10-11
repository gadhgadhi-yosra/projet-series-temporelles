# 2 — Analyse exploratoire

Toutes les analyses de cette section portent sur l'apprentissage (du 1er janvier 2016 au 6 août 2025, 3 506 jours), afin qu'aucune information du test n'intervienne dans les choix de modélisation (notebook `02_eda.ipynb`).

## 2.1 Visualisation de la série

La consommation moyenne est de 1 258,93 GWh/jour pour un écart-type de 252,75 GWh/jour ; elle est asymétrique à droite (skewness 0,69) et plus aplatie qu'une loi normale (kurtosis excédentaire −0,43), ce qui reflète le mélange de jours d'été et d'hiver. La température moyenne nationale est de 13,34 °C (écart-type 6,16 °C).

[[FIG:carpet|../figures/carpet_plot.png|Consommation journalière, un pixel par jour|Les rayures verticales régulières sont les week-ends, les bandes rouges les hivers ; le bleu inhabituel du printemps 2020 correspond au confinement et le refroidissement des couleurs d'hiver à partir de fin 2022 à la sobriété.]]

## 2.2 Décomposition (MSTL)

Une décomposition MSTL sépare la série en tendance, saisonnalité hebdomadaire (7 jours), saisonnalité annuelle (365 jours) et résidu. La force saisonnière vaut **0,90 pour le cycle annuel** et **0,45 pour le cycle hebdomadaire**.

[[FIG:mstl|../figures/mstl.png|Décomposition MSTL de la consommation|La saisonnalité annuelle (environ ±400 GWh/jour) domine ; la saisonnalité hebdomadaire (environ ±100 GWh/jour) abaisse la consommation le week-end ; la tendance montre une baisse en 2020, un rebond en 2021 puis une chute durable fin 2022.]]

Chaque composante se commente ainsi. La **tendance** est stable jusqu'en 2019, baisse en 2020 (confinements), rebondit en 2021 puis chute durablement fin 2022, d'environ 1 310 à 1 200 GWh/jour, sans retour au niveau d'avant la crise énergétique ; ces deux ruptures font l'objet de la section 7.2. La **saisonnalité annuelle** suit le cycle de chauffage. La **saisonnalité hebdomadaire** est nette mais plus modérée. Le **résidu** contient les chocs de météo et d'activité : il sert à détecter les valeurs aberrantes (section 2.4).

## 2.3 Autocorrélations (ACF et PACF)

[[FIG:acf|../figures/acf_pacf.png|ACF et PACF de la série brute, différenciée et doublement différenciée|L'ACF de la série brute décroît lentement avec des bosses tous les 7 jours ; après les différences simple et saisonnière, il ne reste que des pics aux retards 1 et 7.]]

- **Série brute.** L'ACF décroît très lentement (encore environ 0,45 au retard 56) avec des bosses tous les 7 jours : la série n'est pas stationnaire au sens strict et présente une saisonnalité hebdomadaire. La PACF montre un pic d'environ 0,95 au retard 1, puis des pics autour des retards 7 et 8.
- **Après une différence simple (Δ1).** La tendance disparaît, mais l'ACF garde des pics d'environ 0,70 aux retards 7, 14, 21, … qui ne décroissent pas : il reste une non-stationnarité saisonnière de période 7, qui justifie une différence saisonnière (D = 1, s = 7).
- **Après Δ1 et Δ7.** L'ACF retombe dans l'intervalle de confiance, sauf un pic d'environ +0,20 au retard 1 (composante non saisonnière d'ordre 1) et un pic d'environ −0,45 au retard 7 (MA saisonnier d'ordre 1). Les candidats naturels sont donc SARIMA(0,1,1)(0,1,1)[7], SARIMA(1,1,1)(0,1,1)[7] et SARIMA(1,1,0)(0,1,1)[7].
- **Limite.** La saisonnalité annuelle (365 jours) n'est pas captée par s = 7 : elle sera introduite par des régresseurs de calendrier dans les modèles multivariés.

## 2.4 Valeurs aberrantes

Nous appliquons un score z robuste (médiane et écart absolu médian, MAD) au résidu de la décomposition, avec le seuil |z| > 3,5. Il signale **133 jours (3,8 % de l'apprentissage)**, concentrés en hiver (53 en janvier, 24 en février, 22 en décembre). Ce ne sont pas des erreurs de mesure : les sur-consommations correspondent à des vagues de froid (fin février 2018, avec le maximum de 2 150,40 GWh le 28 février 2018) et les sous-consommations au premier confinement (par exemple le lundi de Pâques, 13 avril 2020), à des jours fériés ou à l'hiver doux et sobre de janvier 2023. **Traitement : conservation.** Supprimer ces jours effacerait précisément les chocs que nous voulons modéliser ; ils sont expliqués par les régresseurs de calendrier et de température (`hdd`, `cdd`, `ferie`).

[[FIG:aberrantes|../figures/valeurs_aberrantes.png|Valeurs aberrantes du résidu MSTL|Les jours aberrants se regroupent en hiver, quand la sensibilité à la température est maximale, et au printemps 2020.]]

## 2.5 Stationnarité (ADF et KPSS)

[[TAB:stationnarite|Tests de stationnarité ADF et KPSS|La série brute est stationnaire « à la limite » (KPSS non rejeté à 5 % seulement) ; les séries différenciées sont stationnaires sans ambiguïté.]]

| Série | ADF (statistique) | ADF (p) | KPSS (statistique) | KPSS (p) |
|---|---|---|---|---|
| Consommation brute | −4,10 | 0,001 | 0,40 | 0,076 |
| Différence simple (Δ1) | −12,21 | < 0,001 | 0,02 | > 0,10 |
| Δ1 puis différence saisonnière (Δ1Δ7) | −18,40 | < 0,001 | 0,01 | > 0,10 |
| Température moyenne | −3,48 | 0,009 | 0,08 | > 0,10 |

L'ADF (hypothèse nulle : racine unitaire) rejette la non-stationnarité de la série brute, et le KPSS (hypothèse nulle : stationnarité) ne la rejette pas à 5 % (p = 0,076), mais la rejetterait à 10 % (0,403 > 0,347). Les tests concluent donc à une stationnarité limite, ce qui contraste avec la décroissance lente de l'ACF, que nous attribuons au cycle annuel plutôt qu'à une racine unitaire. Les recommandations automatiques divergent (`ndiffs` : d = 1 selon le KPSS, d = 0 selon l'ADF ; `nsdiffs` : D = 0 selon OCSB, D = 1 selon Canova-Hansen).

**Conclusion sur la différenciation.** Nous retenons **d = 1, D = 1, s = 7** (choix prudent, justifié par la limite du KPSS, par l'ACF lente et par les ruptures de 2020 et 2022), et nous comparons des variantes avec D = 0 ou d = 0 en section 3.1. Pour les modèles multivariés, les deux séries étant stationnaires en niveau, nous estimons le VAR en niveaux (section 3.2).

## 2.6 Relation entre consommation et température

[[FIG:temperature|../figures/conso_vs_temperature.png|Consommation en fonction de la température|La relation est en U très asymétrique : chaque degré en moins sous 15 °C ajoute environ 56,2 GWh/jour, alors que la remontée côté chaud reste faible.]]

La consommation moyenne passe de 1 720 GWh/jour pour une température moyenne comprise entre −5 et 5 °C à 1 041 GWh/jour entre 18 et 21 °C (minimum), puis remonte à 1 104 GWh/jour au-delà de 24 °C. La corrélation avec la consommation est de −0,83 pour la température brute, de 0,89 pour les degrés-jours de chauffage `hdd` (qui linéarisent la relation) et de −0,20 pour `cdd`. Les week-ends forment un nuage décalé vers le bas à température égale, ce qui justifie le jour de la semaine comme variable.
