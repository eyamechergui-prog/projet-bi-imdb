
{{ config(materialized='table') }}

SELECT
    F.film_id AS tconst,
    F.annee_sortie AS annee,
    F.duree_minutes,
    R.note_moyenne,
    R.nb_votes,
    1 AS nombre_films,
    CASE
        WHEN R.note_moyenne IS NOT NULL
        THEN 1
        ELSE 0
    END AS film_note

FROM {{ ref('stg_films') }} F

LEFT JOIN {{ ref('stg_ratings') }} R
    ON F.film_id = R.film_id
