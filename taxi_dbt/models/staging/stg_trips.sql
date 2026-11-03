select
    PULocationID   as pickup_zone_id,
    DOLocationID   as dropoff_zone_id,
    payment_type   as payment_type_id,
    pickup_date,
    trip_distance,
    trip_minutes,
    fare_amount,
    tip_amount,
    total_amount
from {{ source('raw', 'trips') }}
