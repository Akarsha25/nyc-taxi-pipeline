"""Phase 1, Step 1: explore the raw data before building anything.

Real data engineers ALWAYS profile a new source first: how big is it, what columns,
what's broken? You did this for years in ETL QA - now do it in Python + DuckDB.

Run: open this file in VS Code and press Cmd+Shift+B.

How to query a Parquet file with DuckDB (this is the only new thing you need):

    import duckdb
    con = duckdb.connect()
    con.sql("select count(*) from 'data/raw/yellow_tripdata_2024-01.parquet'").show()

DuckDB can read the Parquet file directly, as if it were a table.
"""
import duckdb

RAW = "data/raw/yellow_tripdata_2024-01.parquet"
con = duckdb.connect()

# E1: How many trips are in the file?
#     Output: one number
#     Answer: 2964624
con.sql(f"select count(*) from '{RAW}'").show()


# E2: Show the first 5 rows, so you can see what the data looks like.
#     Output: a 5-row table
#     Answer: 5 rows with columns like tpep_pickup_datetime, trip_distance, fare_amount ...
con.sql(f"select * from '{RAW}' fetch first 5 rows only").show()

# E3: Data-quality report. Count the bad rows of each kind:
#       - negative fare_amount
#       - passenger_count is missing (NULL)
#       - trip_distance is 0
#       - pickup time NOT in January 2024
#       - dropoff time BEFORE pickup time
#     Output: one row: neg_fare | null_passengers | zero_distance | wrong_month | dropoff_before_pickup
#     Example: a trip with fare_amount = -5.0 counts as 1 in neg_fare
#     Answer: 37448 | 140162 | 60371 | 18 | 56
con.sql(f"""select sum(case when fare_amount < 0 then 1 else 0 end) as neg_fare,
                   sum(case when Passenger_count is null then 1 else 0 end) as null_passengers,
                   sum(case when trip_distance=0 then 1 else 0 end ) as Zero_distance,
                   sum(case when  tpep_pickup_datetime < '2024-01-01' or  tpep_pickup_datetime >= '2024-02-01' then 1 else 0 end) as wrong_month,
                   sum(case when  tpep_dropoff_datetime < tpep_pickup_datetime then 1 else 0 end  ) as dropoff_before_pickup
                   from '{RAW}'""").show()
        

# E4: Number of trips and average fare for each payment_type.
#     Output: payment_type | trips | avg_fare (2 decimals), ordered by payment_type
#     Answer: 0 | 140162 | 20.02    1 | 2319046 | 18.56    2 | 439191 | 17.87
#             3 | 19597 | 6.75      4 | 46628 | 1.33
#     (1 = credit card, 2 = cash, 3 = no charge, 4 = dispute, 0 = unknown)

con.sql(f"""select payment_type,count(*) as trips ,round(avg(fare_amount),2) as avg_fare
from '{RAW}'
group by payment_type
order by payment_type""").show()
