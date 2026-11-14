# Schéma dimensionnel IMDb

Le grain de `fait_film` est **une ligne par film** (`tconst`). `dim_film` et `dim_date` sont reliées à la table de faits. La relation films-genres est plusieurs-à-plusieurs et passe par `pont_film_genre`. Le champ `poids` permet un décompte pondéré sans double comptage lorsqu'on agrège sur tous les genres.

```mermaid
erDiagram
    dim_film ||--|| fait_film : "tconst"
    dim_date ||--o{ fait_film : "annee"
    dim_film ||--o{ pont_film_genre : "tconst"
    dim_genre ||--o{ pont_film_genre : "genre_key"
    dim_film {
        varchar tconst PK
        varchar titre
        varchar titre_original
        int adulte
    }
    dim_date {
        int annee PK
        int decennie
    }
    dim_genre {
        int genre_key PK
        varchar nom_genre
    }
    fait_film {
        varchar tconst PK
        int annee FK
        int duree_minutes
        double note_moyenne
        bigint nb_votes
        int nombre_films
        int film_note
    }
    pont_film_genre {
        varchar tconst FK
        int genre_key FK
        double poids
    }
```

**À retenir :** les flèches désignent des relations logiques (et non nécessairement des contraintes SQL physiquement déclarées). Un film n'a pas toujours d'année ou de genre ; les relations facultatives doivent être traitées correctement dans le dashboard. Pour produire `docs/schema_etoile.png`, ouvrir l'aperçu Markdown/Mermaid dans VS Code ou un éditeur Mermaid et exporter le diagramme en PNG.
