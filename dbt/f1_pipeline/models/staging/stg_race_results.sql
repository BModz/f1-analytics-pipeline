with source as (
    select * from {{ source('raw', 'race_results') }}
),

renamed as (
    select
        season,
        round_number,
        event_name,
        event_date,
        circuit,
        country,
        cast(driver_number as string)   as driver_number,
        abbreviation                    as driver_code,
        full_name                       as driver_name,
        team_name,
        cast(position as int64)         as finish_position,
        cast(grid_position as int64)    as grid_position,
        cast(points as float64)         as points,
        status
    from source
)

select * from renamed
