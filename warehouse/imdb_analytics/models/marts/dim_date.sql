
{{ config(materialized='table') }}

SELECT DISTINCT
    annee_sortie AS annee,
    CAST(
        FLOOR(annee_sortie / 10.0) * 10
        AS INTEGER
    ) AS decennie

FROM {{ ref('stg_films') }}

WHERE annee_sortie IS NOT NULL
ORDER BY annee
