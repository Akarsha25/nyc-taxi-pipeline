
select
    LocationID   as zone_id,
    Borough      as borough,
    Zone         as zone_name,
    service_zone
from '../data/raw/taxi_zone_lookup.csv'