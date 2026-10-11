**Lecture d'ensemble.** Je m'appuie uniquement sur les statistiques fournies. Quand je calcule un rapport à partir de ces chiffres, je le signale ; quand une information manque (autocorrélations, graphiques, lien entre consommation et température), je le dis.

**1. Différenciation (d, D)**

- *Série brute.* L'ADF rejette la racine unitaire (statistique −4,10, p-value 0,0010), et le KPSS ne rejette pas la stationnarité au seuil de 5 % (statistique 0,40, p-value 0,0759), mais il la rejetterait au seuil de 10 %. Les deux tests ne se contredisent donc pas formellement à 5 %, mais la conclusion est fragile : la série est « à la limite ».
- *Après Δ1.* ADF −12,21 (p-value 0,0000) et KPSS 0,02 (p-value 0,1000) : stationnarité nette. La p-value de 0,1000 est très probablement la borne supérieure de la table du test, pas une valeur exacte.
- *Après Δ1 puis Δ7.* ADF −18,40 et KPSS 0,01 : stationnarité nette également.
- *Indice par la variance.* La variance passe de 63 882,41 à 7 160,41 après Δ1, puis à 3 601,69 après Δ1 et Δ7 ; elle est donc divisée par environ 9, puis encore par environ 2 (rapports que je calcule). Une variance qui continue de baisser ne signale pas de sur-différenciation, sans le prouver.
- *Hypothèses à tester.* (d = 1, D = 1, s = 7) comme choix prudent ; (d = 0, D = 1, s = 7), puisque l'ADF ne demande pas de différence ordinaire ; (d = 1, D = 0) avec le jour de la semaine en variable explicative.
- *Ce que ces statistiques ne permettent pas de conclure.* L'ADF et le KPSS ne testent pas une racine unitaire saisonnière : le choix de D doit être confirmé par l'ACF aux retards 7, 14, 21 et par un test dédié (OCSB ou Canova-Hansen). Elles ne disent rien non plus d'éventuelles ruptures de niveau, qui peuvent fausser les deux tests.

**2. Familles de modèles**

*SARIMA de période 7.*
- Réglages plausibles : SARIMA(0,1,1)(0,1,1)[7] comme point de départ, puis (1,1,1)(0,1,1)[7], (1,1,0)(0,1,1)[7] et des variantes avec d = 0 ou D = 0.
- Statistique qui motive : la baisse de variance de 7 160,41 à 3 601,69 quand on ajoute la différence de période 7, signe d'une structure hebdomadaire forte.
- Limite : les ordres p, q, P et Q ne peuvent pas être déduits de ces statistiques ; il faut l'ACF et la PACF de la série différenciée, puis un test de Ljung-Box sur les résidus. Une saisonnalité annuelle est vraisemblable pour une consommation électrique, mais rien dans ces chiffres ne la mesure ; une période 7 ne la capterait pas.

*Régression dynamique ou SARIMAX avec température et calendrier.*
- Réglages plausibles : température (éventuellement transformée en degrés-jours), indicatrices de jour de la semaine et de jour férié, termes de Fourier annuels, erreurs ARMA.
- Statistique qui motive : l'étendue de la consommation (de 854,85 à 2 150,40 pour une moyenne de 1 258,93) et l'asymétrie positive (0,69) suggèrent des épisodes de forte consommation qu'une variable externe pourrait expliquer.
- Limite : aucune corrélation entre consommation et température n'est fournie. La forme de la relation (linéaire ou non) est une hypothèse à vérifier par un nuage de points.

*VAR sur la consommation et la température.*
- Réglages plausibles : VAR en niveaux, ordre choisi par AIC et BIC, avec le calendrier en variables exogènes ; test de causalité de Granger dans les deux sens.
- Statistique qui motive : les deux séries apparaissent stationnaires en niveau selon l'ADF (−4,10 et −3,48, p-values 0,0010 et 0,0086) et le KPSS ne rejette pas (p-values 0,0759 et 0,1000).
- Limite : si les deux séries sont stationnaires, il n'y a pas lieu de chercher une cointégration ; un VECM ne se justifie que si elles sont intégrées d'ordre 1. Le test de Johansen trancherait (un rang plein confirmerait la stationnarité).

*GARCH sur les résidus du modèle de moyenne.*
- Réglages plausibles : GARCH(1,1) à loi normale, puis à loi de Student ; ordres supérieurs seulement si les résidus standardisés gardent un effet ARCH.
- Statistique qui motive : le kurtosis excédentaire passe de −0,43 (série brute) à 2,52 après Δ1 et Δ7, ce qui indique des queues plus épaisses que la loi normale pour les variations.
- Limite : un kurtosis élevé peut venir de quelques jours atypiques (jours fériés, vagues de froid) et non d'une volatilité qui se regroupe. Seul un test ARCH-LM sur les résidus, puis l'examen de l'autocorrélation des résidus au carré, permettent de conclure.

*Réseaux récurrents (LSTM, GRU).*
- Réglages plausibles : fenêtre d'entrée de 7 à 28 jours, une couche, quelques dizaines d'unités, entrées normalisées, calendrier en entrée, arrêt anticipé.
- Statistique qui motive : l'écart-type de 252,75 pour une moyenne de 1 258,93 impose une normalisation ; avec 3 506 observations, un petit réseau est préférable à une architecture profonde.
- Limite : ces statistiques ne disent rien de la non-linéarité de la série. Le gain éventuel ne se juge que par une validation croisée temporelle (walk-forward), jamais par un k-fold aléatoire.

*Références et modèle additionnel.*
- Prévision naïve saisonnière (valeur de la semaine précédente) et persistance, indispensables pour situer les autres modèles.
- Prophet ou un modèle à saisonnalités multiples si une saisonnalité annuelle est confirmée par ailleurs.

**3. Ce qu'il me manque pour aller plus loin**

- ACF et PACF de la série brute et différenciée.
- Une décomposition (tendance, saisonnalités) et la présence éventuelle de ruptures.
- Le lien entre consommation et température.
- Les valeurs aberrantes et leur cause.

**4. Protocole conseillé.** Découpage chronologique, mêmes métriques pour tous les modèles, diagnostic de résidus systématique, puis test de Diebold–Mariano avant d'affirmer qu'un modèle est meilleur qu'un autre.
