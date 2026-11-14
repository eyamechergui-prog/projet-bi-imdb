
{{ config(materialized='view') }}

SELECT
    tconst AS film_id,
    TRY_CAST(averageRating AS DOUBLE) AS note_moyenne,
    TRY_CAST(numVotes AS BIGINT) AS nb_votes

FROM {{ source('imdb', 'raw_title_ratings') }}

WHERE tconst IS NOT NULL
