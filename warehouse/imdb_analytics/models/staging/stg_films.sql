
{{ config(materialized='view') }}

SELECT
    tconst AS film_id,
    primaryTitle AS titre,
    originalTitle AS titre_original,
    TRY_CAST(startYear AS INTEGER) AS annee_sortie,
    TRY_CAST(runtimeMinutes AS INTEGER) AS duree_minutes,
    genres,
    TRY_CAST(isAdult AS INTEGER) AS adulte

FROM {{ source('imdb', 'raw_title_basics') }}

WHERE titleType = 'movie'
