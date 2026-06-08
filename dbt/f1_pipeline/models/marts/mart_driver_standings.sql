{{
    config(
        materialized='incremental',
        unique_key=['season', 'round_number', 'driver_code'],
        on_schema_change='sync_all_columns'
    )
}}

with progression as (
    select * from {{ ref('int_championship_progression') }}

    {% if is_incremental() %}
        -- On incremental runs, only process rounds not yet in the table
        where (season, round_number) > (
            select (max(season), max(round_number))
            from {{ this }}
        )
    {% endif %}
)

select * from progression
