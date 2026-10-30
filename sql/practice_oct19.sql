-- SQL practice on your star schema (taxi.duckdb). Run: Cmd+Shift+B. End each query with ;
--
-- ALL TABLES AND COLUMNS
--   fact_trips    : trip_id, pickup_zone_id, dropoff_zone_id, payment_type_id, vendor_id, rate_code_id,
--                   pickup_date, trip_distance, trip_minutes, fare_amount, tip_amount, total_amount
--   dim_zone      : zone_id, borough, zone_name, service_zone
--   dim_date      : date_key, day_name, is_weekend, week_start, month_name, is_holiday, holiday_name
--   dim_payment   : payment_type_id, payment_name
--   dim_vendor    : vendor_id, vendor_name
--   dim_rate_code : rate_code_id, rate_name


-- S1: Which 5 pickup zones made the most money?
--     Output:  zone_name | revenue
--     Answer:  JFK Airport 11166124.94, LaGuardia Airport 5790026.95, Midtown Center 3271244.79,
--              Upper East Side South 2703925.64, Times Sq/Theatre District 2685458.07

select Z.zone_name,round(sum(t.total_amount),2) as revenue
from dim_zone z
join fact_trips t
on z.zone_id=t.pickup_zone_id
group by Z.zone_name;
-- S2: Weekday vs weekend: number of trips and average total_amount.
--     Output: is_weekend | trips | avg_total (2 decimals)
--     Example: join fact_trips to dim_date on pickup_date = date_key
--     Answer: false | 2056181 | 27.78      true | 698689 | 26.19

select d.is_weekend,count(t.trip_id) as trips,round(avg(total_amount),2) as avg_total
from fact_trips t
join dim_date d
on t.pickup_date=d.date_key
group by d.is_weekend;