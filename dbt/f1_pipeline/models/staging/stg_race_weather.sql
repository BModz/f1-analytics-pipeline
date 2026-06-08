with source as (
    select * from {{ source('raw', 'race_weather') }}
),

renamed as (
    select
        season,
        round_number,
        event_name,
        circuit,
        cast(time as float64)           as session_time_seconds,
        cast(air_temp as float64)       as air_temp_c,
        cast(track_temp as float64)     as track_temp_c,
        cast(humidity as float64)       as humidity_pct,
        cast(pressure as float64)       as pressure_mbar,
        cast(wind_speed as float64)     as wind_speed_ms,
        cast(wind_direction as int64)   as wind_direction_deg,
        cast(rainfall as bool)          as is_raining
    from source
)

select * from renamed
