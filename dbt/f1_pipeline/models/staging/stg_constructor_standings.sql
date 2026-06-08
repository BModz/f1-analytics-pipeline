with source as (
    select * from {{ source('raw', 'constructor_standings') }}
),

renamed as (
    select
        season,
        round_number,
        constructor_id,
        constructor_name,
        position        as championship_position,
        points          as cumulative_points,
        wins            as cumulative_wins
    from source
)

select * from renamed
