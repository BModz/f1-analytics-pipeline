{% snapshot snap_driver_standings %}

{{
    config(
        target_schema='snapshots',
        unique_key='season || \'-\' || round_number || \'-\' || driver_code',
        strategy='check',
        check_cols=['championship_position', 'cumulative_points', 'cumulative_wins'],
    )
}}

select * from {{ ref('stg_driver_standings') }}

{% endsnapshot %}
