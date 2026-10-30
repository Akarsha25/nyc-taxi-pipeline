"""Phase 2: build the star schema in taxi.duckdb.

Why: one wide table repeats descriptions and hides meaning (PULocationID = 161 means nothing).
A star schema = one FACT table (events + numbers) + small DIMENSION tables (descriptions).
Grain of our fact table: ONE ROW = ONE TRIP.

        dim_zone
           |
 dim_payment -- fact_trips -- dim_date
                /         \\
        dim_vendor     dim_rate_code

Run: open this file in VS Code and press Cmd+Shift+B.
"""
import duckdb

ZONES = "data/raw/taxi_zone_lookup.csv"
con = duckdb.connect("taxi.duckdb")

# M1: Create the dimension table dim_zone from the zone file (columns: LocationID, Borough, Zone, service_zone).
#     Rename the columns:  LocationID -> zone_id,  Borough -> borough,  Zone -> zone_name,  service_zone stays
#     Output: table dim_zone with 4 columns
#     Example: con.sql(f"create or replace table dim_zone as select LocationID as zone_id, ... from '{ZONES}'")
#     Answer: 265 rows.  zone_id 161 -> Manhattan | Midtown Center

con.sql(f"""create or replace table dim_zone as 
select LocationID as zone_id,
Borough as borough,
Zone as zone_name,
service_zone
from  '{ZONES}'""")

print(con.sql(f"select count(*) from dim_zone").fetchone()[0])


# M2: Create the dimension table dim_payment. There is no file for it - type the values in with VALUES:
#         0 Flex fare, 1 Credit card, 2 Cash, 3 No charge, 4 Dispute, 5 Unknown, 6 Voided trip
#     Output: table dim_payment(payment_type_id, payment_name)
#     Example: con.sql("""create or replace table dim_payment as
#                         select * from (values (0, 'Flex fare'), (1, 'Credit card')) as t(payment_type_id, payment_name)""")
#              (add the other 5 rows)
#     Answer: 7 rows

con.sql(f"""create or replace table dim_payment as
select * from (values
(0,'Flex fare'),
(1,'Credit Card'),
(2,'Cash'),
(3,'No Charge'),
(4,'Dispute'),
(5,'Unknown'),
(6,'Voided trip')
) as t(payment_type_id,payment_name)""")
print(con.sql(f"select count(*) from dim_payment").fetchone()[0])


# M2b: Create dim_vendor (the company that sent the trip record). Type the values with VALUES:
#          1 Creative Mobile Technologies, 2 Curb Mobility
#      Output: table dim_vendor(vendor_id, vendor_name)
#      Answer: 2 rows

con.sql(f""" create or replace table dim_vendor as
select * from (values 
('1','Creative Mobile Technologies'),
('2','Curb Mobility')) as t(vendor_id,vendor_name)""")
print(con.sql(f"select count(*) from dim_vendor").fetchone()[0])


# M2c: Create dim_rate_code (the kind of fare). Type the values with VALUES:
#          1 Standard rate, 2 JFK airport, 3 Newark airport, 4 Nassau or Westchester,
#          5 Negotiated fare, 6 Group ride, 99 Unknown
#      Output: table dim_rate_code(rate_code_id, rate_name)
#      Answer: 7 rows
con.sql(f""" create or replace table dim_rate_code as
select * from (values
(1,'Standard rate'),
(2,'JFK airport'),
(3,'Newark airport'),
(4,'Nassau or Westchester'),
(5,'Negotiated fare'),
(6,'Group ride'),
(99,'Unknown') )as t(rate_code_id,rate_name)""")

print(con.sql(f"select count(*) from dim_rate_code").fetchone()[0])


# M2d: Create dim_date: one row per day of January 2024, with useful descriptions.
#      Make the days with generate_series, then add columns:
#          date_key     -> the date
#          day_name     -> dayname(date_key)                      e.g. Monday
#          is_weekend   -> dayofweek(date_key) in (0, 6)          (0 = Sunday, 6 = Saturday)
#          week_start   -> date_trunc('week', date_key)
#          is_holiday   -> date_key in ('2024-01-01', '2024-01-15')   (New Year's Day, Martin Luther King Jr. Day)
#      Example: con.sql("""create or replace table dim_date as
#                          select cast(d as date) as date_key, dayname(d) as day_name, ...
#                          from generate_series(date '2024-01-01', date '2024-01-31', interval 1 day) as g(d)""")
#      Answer: 31 rows, 8 weekend days, 2 holidays.  2024-01-01 -> Monday | weekend false | holiday true


con.sql("""
    create or replace table dim_date as
    with holidays as (
        select * from (values
            (date '2024-01-01', 'New Year''s Day'),
            (date '2024-01-15', 'Martin Luther King Jr. Day'),
            (date '2024-02-19', 'Presidents Day'),
            (date '2024-05-27', 'Memorial Day'),
            (date '2024-06-19', 'Juneteenth'),
            (date '2024-07-04', 'Independence Day'),
            (date '2024-09-02', 'Labor Day'),
            (date '2024-10-14', 'Columbus Day'),
            (date '2024-11-11', 'Veterans Day'),
            (date '2024-11-28', 'Thanksgiving'),
            (date '2024-12-25', 'Christmas Day')
        ) as t(holiday_date, holiday_name)
    )
    select cast(g.d as date)                      as date_key,
           dayname(g.d)                           as day_name,
           dayofweek(g.d) in (0, 6)               as is_weekend,
           cast(date_trunc('week', g.d) as date)  as week_start,
           monthname(g.d)                         as month_name,
           h.holiday_name is not null             as is_holiday,
           h.holiday_name
    from generate_series(date '2024-01-01', date '2024-12-31', interval 1 day) as g(d)
    left join holidays h on h.holiday_date = cast(g.d as date)
""")

print(con.sql("select count(*), sum(case when is_holiday then 1 else 0 end) from dim_date").fetchone())


# M3: Create the fact table fact_trips from trips. Keep only KEYS and MEASURES:
#       keys:     trip_id (new: row_number() over ()), PULocationID as pickup_zone_id, DOLocationID as dropoff_zone_id,
#                 payment_type as payment_type_id, VendorID as vendor_id, RatecodeID as rate_code_id,
#                 pickup_date (links to dim_date.date_key)
#       measures: trip_distance, trip_minutes, fare_amount, tip_amount, total_amount
#     Output: table fact_trips with 12 columns
#     Answer: 2754870 rows

con.sql("""create or replace table fact_trips as 
select row_number() over () as trip_id,
PULocationID as pickup_zone_id,
DOLocationID as dropoff_zone_id,
payment_type as payment_type_id,
VendorID as vendor_id,
RatecodeID as rate_code_id,
pickup_date,
trip_distance,
trip_minutes,
fare_amount,
tip_amount,
total_amount
from trips""")

print(con.sql(f"select count(*) from fact_trips").fetchone()[0])


# M4: Use the star! Number of trips per PICKUP borough, highest first.
#     Join fact_trips to dim_zone on pickup_zone_id = zone_id.
#     Output: borough | trips
#     Answer: Manhattan 2469613, Queens 253523, Brooklyn 16761, Unknown 9480, Bronx 4941,
#             N/A 473, EWR 50, Staten Island 29
con.sql(""" select z.borough,count(*) as trips
from fact_trips t
join dim_zone z
on t.pickup_zone_id=z.Zone_id
group by z.borough
order by trips desc""").show()