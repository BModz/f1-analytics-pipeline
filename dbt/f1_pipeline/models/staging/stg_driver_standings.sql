with source as (
    select * from {{ source('raw', 'driver_standings') }}
),

renamed as (
    select
        season,
        round_number,
        driver_id,
        driver_code,
        position        as championship_position,
        points          as cumulative_points,
        wins            as cumulative_wins
    from source
)

select * from renamed
