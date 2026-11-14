
import duckdb
from pathlib import Path

# Chemin du projet
BASE_DIR = Path(__file__).resolve().parent

# Connexion à DuckDB
db_path = BASE_DIR / "warehouse/imdb_analytics/dev.duckdb"

con = duckdb.connect(str(db_path), read_only=True)

try:
    # Jointure entre les films et les notes
    resultat = con.execute("""
        SELECT
            F.film_id,
            F.titre,
            F.annee_sortie,
            R.note_moyenne,
            R.nb_votes
        FROM main.stg_films F
        INNER JOIN main.stg_ratings R
            ON F.film_id = R.film_id
        LIMIT 10
    """).df()

    print("\n===== FILMS AVEC NOTES IMDb =====")
    print(resultat.to_string(index=False))

finally:
    con.close()
