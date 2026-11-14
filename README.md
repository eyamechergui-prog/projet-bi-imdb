# IMDb Analytics — Système décisionnel pour l'analyse du succès des films

## Présentation
Projet de Business Intelligence basé sur les données non commerciales IMDb. Il couvre l'ingestion, l'exploration, la modélisation dimensionnelle, les contrôles de qualité, la visualisation interactive et une expérimentation de prédiction de la note moyenne IMDb.

## Objectifs
- Analyser le nombre de films, les notes et les votes.
- Étudier les tendances par année, décennie et genre.
- Construire un entrepôt de données en étoile avec DuckDB et dbt.
- Développer un tableau de bord interactif avec Streamlit et Plotly.
- Comparer une baseline à un modèle Random Forest sur des films plus récents.

## Technologies
Python 3.11, DuckDB, dbt-duckdb, pandas, Streamlit, Plotly, scikit-learn, Jupyter et joblib.

## Sources IMDb
- `title.basics.tsv` ou `title.basics.tsv.gz`
- `title.ratings.tsv.gz`

Données fournies par IMDb pour un usage non commercial, sous réserve de leurs conditions d'utilisation. Télécharger les fichiers depuis https://datasets.imdbws.com/ et consulter https://developer.imdb.com/non-commercial-datasets/.

## Pipeline
1. Ingestion de `title.basics` et `title.ratings` dans `dev.duckdb` via `charger_imdb.py`.
2. Exploration SQL via `explorer_imdb.py`.
3. Modèles dbt de staging : `stg_films`, `stg_ratings`.
4. Modèles analytiques : `dim_film`, `dim_date`, `dim_genre`, `pont_film_genre`, `fait_film`.
5. Tests de qualité dbt.
6. Analyse interactive avec `app.py`.
7. Préparation et évaluation d'un modèle Random Forest dans `notebooks/prediction.ipynb`.

## Résultats observés
- Titres IMDb chargés : **12 958 477**.
- Titres notés chargés : **1 731 756**.
- Films (`titleType = 'movie'`) : **760 795**.
- Films notés : **351 716**.
- Note moyenne des films notés : **6,15/10**.
- Total des votes sur les films : **1 308 501 754**.
- Tests dbt : **16/16 réussis** (sur les règles configurées).

Résultats de prédiction sur une séparation temporelle (entraînement avant 2015, test à partir de 2015) :

| Modèle | MAE | R² |
|---|---:|---:|
| Baseline (moyenne) | 1,2140 | -0,0049 |
| Random Forest | 0,9996 | 0,2542 |

Les chiffres correspondent à une extraction IMDb donnée et peuvent évoluer lors d'un nouveau téléchargement.

## Installation et exécution (Windows / Git Bash)
```bash
cd ~/Desktop/projet_BISirine
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

Télécharger les fichiers IMDb dans `data/raw/`, puis exécuter :

```bash
python charger_imdb.py
cd warehouse/imdb_analytics
dbt debug
dbt run --select stg_films stg_ratings dim_film dim_date dim_genre pont_film_genre fait_film
dbt test --select dim_film dim_date dim_genre pont_film_genre fait_film
cd ../..
python -m streamlit run app.py
```

**Remarque :** la connexion dbt peut dépendre de `~/.dbt/profiles.yml` généré localement par `dbt init`. Le fichier DuckDB et les données brutes ne sont pas inclus dans le dépôt.

## Dashboard
Pages : Vue globale, Analyse des genres, Analyse temporelle, Classement des films, Qualité des données et Prédiction ML (si `models_ml/modele_imdb.pkl` existe).

## Modèle dimensionnel
Voir `docs/schema_etoile.md` et exporter son schéma en image pour le rapport.

## Limites
- Les notes IMDb reflètent les évaluations des utilisateurs, pas le revenu commercial ni la rentabilité.
- Un film peut appartenir à plusieurs genres : les décomptes par genre se recouvrent.
- Années, durées et genres peuvent manquer ; les visualisations par année excluent les années nulles.
- Les données IMDb sont une photographie actuelle, pas un historique des informations disponibles avant chaque sortie.
- Random Forest utilise seulement l'année, la durée et les genres ; sa capacité prédictive reste limitée (R² = 0,2542 sur le test observé).
- L'évaluation ML s'appuie sur les films notés et renseignés en année et durée ; elle ne représente pas nécessairement tous les films.
- Les futures années et les productions non finalisées peuvent déformer les tendances.

## Sécurité et versionnement
Ne pas publier les données IMDb brutes, `dev.duckdb`, les environnements virtuels ni les fichiers secrets. Ne charger que des fichiers `joblib` de confiance.
