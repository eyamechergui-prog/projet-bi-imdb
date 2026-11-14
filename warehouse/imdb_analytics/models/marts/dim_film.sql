
{{ config(materialized='table') }}

SELECT
    film_id AS tconst,
    titre,
    titre_original,
    adulte

FROM {{ ref('stg_films') }}
