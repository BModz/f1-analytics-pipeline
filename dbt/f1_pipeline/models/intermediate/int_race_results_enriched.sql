with race_results as (
    select * from {{ ref('stg_race_results') }}
),

drivers as (
    select
        season,
        driver_code,
        nationality         as driver_nationality,
        date_of_birth,
        permanent_number
    from {{ ref('stg_drivers') }}
),

enriched as (
    select
        r.season,
        r.round_number,
        r.event_name,
        r.event_date,
        r.circuit,
        r.country,
        r.driver_number,
        r.driver_code,
        r.driver_name,
        d.driver_nationality,
        d.date_of_birth,
        r.team_name,
        r.finish_position,
        r.grid_position,
        r.finish_position - r.grid_position   as positions_gained,
        r.points,
        r.status,
        r.status != 'Finished'                as did_not_finish
    from race_results r
    left join drivers d
        on r.season = d.season
        and r.driver_code = d.driver_code
)

select * from enriched
