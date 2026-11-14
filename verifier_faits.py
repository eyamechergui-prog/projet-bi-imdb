
import duckdb
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

db_path = BASE_DIR / "warehouse/imdb_analytics/dev.duckdb"

con = duckdb.connect(str(db_path), read_only=True)

try:
    resultat = con.execute("""
        SELECT
            COUNT(*) AS total_films,
            SUM(film_note) AS films_notes,
            SUM(nombre_films) AS nombre_films,
            ROUND(AVG(note_moyenne), 2) AS note_moyenne,
            SUM(COALESCE(nb_votes, 0)) AS total_votes
        FROM main.fait_film
    """).df()

    print("\n===== VERIFICATION TABLE DE FAITS =====")
    print(resultat.to_string(index=False))

finally:
    con.close()
