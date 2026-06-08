with source as (
    select * from {{ source('raw', 'constructors') }}
),

renamed as (
    select
        season,
        constructor_id,
        name            as constructor_name,
        nationality
    from source
)

select * from renamed
