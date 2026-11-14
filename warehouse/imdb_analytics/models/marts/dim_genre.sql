
{{ config(materialized='table') }}

WITH genres_separes AS (
    SELECT DISTINCT
        TRIM(genre.nom_genre) AS nom_genre
    FROM {{ ref('stg_films') }} f,
    UNNEST(STRING_SPLIT(f.genres, ',')) AS genre(nom_genre)
    WHERE f.genres IS NOT NULL
)

SELECT
    ROW_NUMBER() OVER (
        ORDER BY nom_genre
    ) AS genre_key,
    nom_genre
FROM genres_separes
WHERE nom_genre <> ''
