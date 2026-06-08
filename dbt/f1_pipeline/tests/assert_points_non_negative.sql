-- Fails if any driver has negative points in any race result.
-- Points are always 0 or positive in F1.
select *
from {{ ref('mart_race_results') }}
where points < 0
