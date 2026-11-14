
import duckdb
from pathlib import Path

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent

# Connexion à la base DuckDB
db_path = BASE_DIR / "warehouse/imdb_analytics/dev.duckdb"
con = duckdb.connect(str(db_path), read_only=True)

try:
    # 1. Afficher les 5 premiers titres
    print("\n===== PREMIERS TITRES IMDb =====")
    films = con.execute("""
        SELECT
            tconst,
            titleType,
            primaryTitle,
            startYear,
            genres
        FROM raw_title_basics
        LIMIT 5
    """).df()

    print(films.to_string(index=False))

    # 2. Afficher les 5 premières notes
    print("\n===== PREMIERES NOTES IMDb =====")
    notes = con.execute("""
        SELECT
            tconst,
            averageRating,
            numVotes
        FROM raw_title_ratings
        LIMIT 5
    """).df()

    print(notes.to_string(index=False))

    # 3. Compter les titres par catégorie
    print("\n===== REPARTITION PAR TYPE =====")
    types = con.execute("""
        SELECT
            titleType,
            COUNT(*) AS nombre
        FROM raw_title_basics
        GROUP BY titleType
        ORDER BY nombre DESC
    """).df()

    print(types.to_string(index=False))

    # 4. Nombre total de films
    print("\n===== NOMBRE TOTAL DE FILMS =====")

    resultat = con.execute("""
        SELECT COUNT(*) AS nombre_films
        FROM raw_title_basics
        WHERE titleType = 'movie'
    """).df()

    print(resultat.to_string(index=False))

    # 5. Nombre de films ayant une note IMDb
    print("\n===== FILMS AVEC NOTES =====")

    resultat = con.execute("""
        SELECT COUNT(*) AS films_notes
        FROM raw_title_basics B
        INNER JOIN raw_title_ratings R
            ON B.tconst = R.tconst
        WHERE B.titleType = 'movie'
    """).df()

    print(resultat.to_string(index=False))

    # 6. Vérifier les données manquantes
    print("\n===== VALEURS MANQUANTES =====")

    resultat = con.execute("""
        SELECT
            COUNT(*) AS total_films,
            COUNT(*) FILTER (
                WHERE startYear IS NULL
            ) AS annee_manquante,
            COUNT(*) FILTER (
                WHERE genres IS NULL
            ) AS genre_manquant,
            COUNT(*) FILTER (
                WHERE runtimeMinutes IS NULL
            ) AS duree_manquante
        FROM raw_title_basics
        WHERE titleType = 'movie'
    """).df()

    print(resultat.to_string(index=False))


finally:
    con.close()
