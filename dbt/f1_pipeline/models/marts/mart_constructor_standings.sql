{{
    config(
        materialized='table'
    )
}}

with constructor_standings as (
    select * from {{ ref('stg_constructor_standings') }}
),

constructors as (
    select
        season,
        constructor_id,
        nationality     as constructor_nationality
    from {{ ref('stg_constructors') }}
),

race_meta as (
    select
        season,
        round_number,
        event_name,
        event_date
    from {{ ref('stg_race_results') }}
    qualify row_number() over (
        partition by season, round_number
        order by finish_position
    ) = 1
),

joined as (
    select
        cs.season,
        cs.round_number,
        r.event_name,
        r.event_date,
        cs.constructor_id,
        cs.constructor_name,
        c.constructor_nationality,
        cs.championship_position,
        cs.cumulative_points,
        cs.cumulative_wins,
        cs.cumulative_points - lag(cs.cumulative_points) over (
            partition by cs.season, cs.constructor_id
            order by cs.round_number
        )                               as points_this_round
    from constructor_standings cs
    left join constructors c
        on cs.season = c.season
        and cs.constructor_id = c.constructor_id
    left join race_meta r
        on cs.season = r.season
        and cs.round_number = r.round_number
)

select * from joined
