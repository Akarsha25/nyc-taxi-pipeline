select
    PULocationID   as pickup_zone_id,
    DOLocationID   as dropoff_zone_id,
    payment_type   as payment_type_id,
    cast(tpep_pickup_datetime as date) pickup_date,
    date_diff('minute',tpep_pickup_datetime,tpep_dropoff_datetime) as trip_minutes,
    trip_distance,
  
    fare_amount,
    tip_amount,
    total_amount
from '../data/raw/yellow_tripdata_2024-01.parquet'
where fare_amount >= 0
and passenger_count is not null
and trip_distance >0
and tpep_pickup_datetime >='2024-01-01'
and tpep_pickup_datetime < '2024-02-01'
and tpep_dropoff_datetime >= tpep_pickup_datetime
