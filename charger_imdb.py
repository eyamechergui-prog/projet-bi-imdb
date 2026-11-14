
import duckdb
from pathlib import Path

# 1. Définir le chemin principal
BASE_DIR = Path(__file__).resolve().parent

# 2. Définir les fichiers IMDb
fichier_films = BASE_DIR / "data/raw/title.basics.tsv"

# Choisir automatiquement le fichier des notes
fichier_notes_gz = BASE_DIR / "data/raw/title.ratings.tsv.gz"
fichier_notes_tsv = BASE_DIR / "data/raw/title.ratings.tsv"

if fichier_notes_gz.exists():
    fichier_notes = fichier_notes_gz
else:
    fichier_notes = fichier_notes_tsv

# 3. Vérifier les fichiers
for fichier in [fichier_films, fichier_notes]:
    if not fichier.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {fichier}"
        )

# 4. Connexion à DuckDB
db_path = BASE_DIR / "warehouse/imdb_analytics/dev.duckdb"
con = duckdb.connect(str(db_path))

try:
    # 5. Charger les informations IMDb
    print("Chargement des titres IMDb...")

    con.execute("""
        CREATE OR REPLACE TABLE raw_title_basics AS
        SELECT *
        FROM read_csv(
            ?,
            delim='\t',
            header=true,
            all_varchar=true,
            nullstr='\\N'
        )
    """, [str(fichier_films)])

    print("Titres chargés !")

    # 6. Charger les notes IMDb
    print("Chargement des notes IMDb...")

    con.execute("""
        CREATE OR REPLACE TABLE raw_title_ratings AS
        SELECT *
        FROM read_csv(
            ?,
            delim='\t',
            header=true,
            all_varchar=true,
            nullstr='\\N'
        )
    """, [str(fichier_notes)])

    print("Notes chargées !")

    # 7. Vérifier les résultats
    nb_titres = con.execute("""
        SELECT COUNT(*)
        FROM raw_title_basics
    """).fetchone()[0]

    nb_notes = con.execute("""
        SELECT COUNT(*)
        FROM raw_title_ratings
    """).fetchone()[0]

    print("\n===== RESULTATS =====")
    print("Nombre de titres :", nb_titres)
    print("Nombre de titres notés :", nb_notes)
    print("Chargement terminé avec succès !")

finally:
    con.close()
