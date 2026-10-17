"""Phase 1, Step 2: the cleaning (ingestion) script.

Your E3 checks from explore.py become the cleaning rules:
a row is GOOD only if it passes ALL 5 checks. Good rows are saved; bad rows are counted.

Run: open this file in VS Code and press Cmd+Shift+B.
"""
import duckdb

RAW = "data/raw/yellow_tripdata_2024-01.parquet"
CLEAN = "data/processed/yellow_tripdata_2024-01_clean.parquet"
con = duckdb.connect()

# I1: Count all rows in the raw file and save the number in a Python variable called rows_in.
#     Hint: .fetchone()[0] gives you the number itself (instead of .show(), which only prints it).
#     Example: rows_in = con.sql(f"select count(*) from '{RAW}'").fetchone()[0]
#     Answer: rows_in = 2964624
rows_in=con.sql(f"select count(*) from '{RAW}'").fetchone()[0]
print(rows_in)


# I2: Count the GOOD rows: rows that pass ALL 5 checks. Save it in a variable called rows_good.
#     Good = fare_amount >= 0
#            AND passenger_count is not null
#            AND trip_distance > 0
#            AND pickup >= '2024-01-01' AND pickup < '2024-02-01'
#            AND dropoff >= pickup
#     Answer: rows_good = 2754870
rows_good = con.sql(f"""
    select count(*)
    from '{RAW}'
    where fare_amount >= 0
      and passenger_count is not null
      and trip_distance > 0
      and tpep_pickup_datetime >= '2024-01-01'
      and tpep_pickup_datetime <  '2024-02-01'
      and tpep_dropoff_datetime >= tpep_pickup_datetime
""").fetchone()[0]
print(rows_good)


# I3: Save the good rows to the CLEAN file. DuckDB writes Parquet with COPY:
#         con.sql(f"copy (select ... from '{RAW}' where ...) to '{CLEAN}' (format parquet)")
#     Answer: a new file appears in data/processed/
con.sql(f""" copy(select * from '{RAW}' where 
 fare_amount >= 0
          and passenger_count is not null
          and trip_distance > 0
          and tpep_pickup_datetime >= '2024-01-01'
          and tpep_pickup_datetime <  '2024-02-01'
          and tpep_dropoff_datetime >= tpep_pickup_datetime) to '{CLEAN}'(format Parquet)""")

print(con.sql(f"select * from '{CLEAN}'").show())



# I4: Print a short report:
#         Rows in:       2964624
#         Rows kept:     2754870
#         Rows rejected: 209754  (7.1%)
#     Hint: rejected = rows_in - rows_good ; percent = rejected * 100 / rows_in
rejected=rows_in-rows_good
print(f"Rows in:{rows_in}")
print(f"Rows_Kept:{rows_good}")
print(f"Rows Rejected:{rejected}({rejected *100/rows_in:.1f}%)")