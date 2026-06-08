with standings as (
    select * from {{ ref('stg_driver_standings') }}
),

drivers as (
    select
        season,
        driver_code,
        full_name           as driver_name,
        nationality         as driver_nationality
    from {{ ref('stg_drivers') }}
),

race_results as (
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
        s.season,
        s.round_number,
        r.event_name,
        r.event_date,
        s.driver_id,
        s.driver_code,
        d.driver_name,
        d.driver_nationality,
        s.championship_position,
        s.cumulative_points,
        s.cumulative_wins,
        lag(s.championship_position) over (
            partition by s.season, s.driver_code
            order by s.round_number
        )                               as prev_championship_position,
        s.cumulative_points - lag(s.cumulative_points) over (
            partition by s.season, s.driver_code
            order by s.round_number
        )                               as points_this_round
    from standings s
    left join drivers d
        on s.season = d.season
        and s.driver_code = d.driver_code
    left join race_results r
        on s.season = r.season
        and s.round_number = r.round_number
)

select * from joined
