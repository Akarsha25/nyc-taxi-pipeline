"""Phase 1, Step 3: load the clean data into a real database.

Until now, DuckDB read the Parquet FILE directly. Now we create a DATABASE FILE (taxi.duckdb)
with a TABLE called trips, so analysts (and later dbt and the AI agent) can just write: from trips

Run: open this file in VS Code and press Cmd+Shift+B.
"""
import duckdb

CLEAN = "data/processed/yellow_tripdata_2024-01_clean.parquet"

# L1: Connect to a database FILE instead of memory.
#     Output: a file taxi.duckdb appears in the project folder after running
#     Example: con = duckdb.connect("taxi.duckdb")      (duckdb.connect() with nothing = memory only, gone when the script ends)
con = duckdb.connect("taxi.duckdb")

# L2: Create the table trips from the clean file, with 2 extra columns:
#       pickup_date  = the pickup time as a date only        -> cast(tpep_pickup_datetime as date)
#       trip_minutes = minutes between pickup and dropoff    -> date_diff('minute', tpep_pickup_datetime, tpep_dropoff_datetime)
#     Use CREATE OR REPLACE so running the script twice gives the same table (no duplicate rows).
#     Example: con.sql(f"create or replace table trips as select *, <extra columns> from '{CLEAN}'")
#     Answer: the table trips exists

con.sql(f"""
    create or replace table trips as
    select *,
           cast(tpep_pickup_datetime as date)                                as pickup_date,
           date_diff('minute', tpep_pickup_datetime, tpep_dropoff_datetime)  as trip_minutes
    from '{CLEAN}'
""")


# L3: Print a load summary: the row count, the number of different pickup dates, and the average trip_minutes.
#     Output: one line, e.g.  Loaded 2754870 trips over 31 days, average 15.7 minutes
#     Answer: 2754870 | 31 | 15.7
rows,days,avg_min=con.sql(f""" select count(*) ,count(distinct pickup_date),round(avg(trip_minutes),1)
from trips""").fetchone()
print(f"Loaded {rows} trips over {days},average{avg_min} minutes")