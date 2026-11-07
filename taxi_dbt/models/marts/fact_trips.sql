select
    row_number() over () as trip_id,
    pickup_zone_id,
    dropoff_zone_id,
    payment_type_id,
    pickup_date,
    trip_distance,
    trip_minutes,
    fare_amount,
    tip_amount,
    total_amount
from {{ ref('stg_trips') }}