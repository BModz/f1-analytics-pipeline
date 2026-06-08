{{
    config(
        materialized='table'
    )
}}

with enriched as (
    select * from {{ ref('int_race_results_enriched') }}
),

final as (
    select
        season,
        round_number,
        event_name,
        event_date,
        circuit,
        country,
        driver_code,
        driver_name,
        driver_nationality,
        team_name,
        finish_position,
        grid_position,
        positions_gained,
        points,
        status,
        did_not_finish,
        -- Podium flag for easy filtering in dashboards
        finish_position <= 3            as is_podium,
        finish_position = 1             as is_winner
    from enriched
)

select * from final
