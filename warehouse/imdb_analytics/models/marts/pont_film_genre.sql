
{{ config(materialized='table') }}

WITH genres_films AS (
    SELECT DISTINCT
        f.film_id AS tconst,
        TRIM(genre.nom_genre) AS nom_genre
    FROM {{ ref('stg_films') }} f,
    UNNEST(STRING_SPLIT(f.genres, ',')) AS genre(nom_genre)
    WHERE f.genres IS NOT NULL
)

SELECT
    gf.tconst,
    dg.genre_key,
    1.0 / COUNT(*) OVER (
        PARTITION BY gf.tconst
    ) AS poids

FROM genres_films gf

INNER JOIN {{ ref('dim_genre') }} dg
    ON gf.nom_genre = dg.nom_genre

WHERE gf.nom_genre <> ''
