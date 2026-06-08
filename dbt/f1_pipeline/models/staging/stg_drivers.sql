with source as (
    select * from {{ source('raw', 'drivers') }}
),

renamed as (
    select
        season,
        driver_id,
        driver_code,
        cast(permanent_number as int64)  as permanent_number,
        given_name,
        family_name,
        full_name,
        cast(date_of_birth as date)      as date_of_birth,
        nationality
    from source
)

select * from renamed
