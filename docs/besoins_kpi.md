
# Projet BI Cinéma IMDb

## 1. Objectif

Concevoir un système décisionnel permettant
d'analyser le succès des films à partir des
données IMDb.

## 2. Sources de données

- title.basics.tsv
- title.ratings.tsv.gz

## 3. Indicateurs KPI

### KPI 1 - Nombre total de films
Nombre de titres dont titleType = 'movie'.

### KPI 2 - Nombre de films notés
Nombre de films possédant une note IMDb.

### KPI 3 - Note moyenne IMDb
Moyenne des notes des films notés.

### KPI 4 - Nombre total de votes
Somme des votes des films.

### KPI 5 - Nombre de films par année
Évolution de la production cinématographique.

### KPI 6 - Note moyenne par genre
Comparaison des genres cinématographiques.

### KPI 7 - Top 10 des films
Classement des films selon leur note IMDb,
avec un seuil minimum de votes à définir.

## 4. Dimensions d'analyse

- Film
- Année
- Genre

## 5. Outil de visualisation

Power BI Desktop

## 6. Outils de transformation

DuckDB et dbt
