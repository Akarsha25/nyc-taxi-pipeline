-- PHASE 2: BUSINESS REPORTS on the star schema (January 2024 yellow taxi trips)
-- Run:  .venv/bin/python run_sql.py sql/reports.sql
--
-- ===================== ALL TABLES AND COLUMNS =====================
-- fact_trips (trip_id, pickup_zone_id, dropoff_zone_id, payment_type_id, vendor_id, rate_code_id,
--             pickup_date, trip_distance, trip_minutes, fare_amount, tip_amount, total_amount)     2,754,870 rows
-- dim_zone (zone_id, borough, zone_name, service_zone)                                             265 rows
-- dim_date (date_key, day_name, is_weekend, week_start, month_name, is_holiday, holiday_name)      366 rows
-- dim_payment (payment_type_id, payment_name)
-- dim_vendor (vendor_id, vendor_name)
-- dim_rate_code (rate_code_id, rate_name)
--
-- Joins: fact_trips.pickup_zone_id -> dim_zone.zone_id      fact_trips.pickup_date -> dim_date.date_key
--        fact_trips.payment_type_id -> dim_payment.payment_type_id
-- ==================================================================


-- R1. Daily revenue: for each day, how many trips and how much total revenue (total_amount, 2 decimals)?
--     Output: pickup_date, trips, revenue      (sorted by date; 31 rows)
--     Answer (first 3 rows): 2024-01-01 68127 2123813.69 | 2024-01-02 71167 2201670.29 | 2024-01-03 78229 2287854.06



-- R2. Top 5 pickup zones by total revenue, with their borough.
--     Output: zone_name, borough, revenue
--     Answer: JFK Airport, Queens, 11166124.94 | LaGuardia Airport, Queens, 5790026.95 | Midtown Center, Manhattan, 3271244.79
--             | Upper East Side South, Manhattan, 2703925.64 | Times Sq/Theatre District, Manhattan, 2685458.07



-- R3. Weekday vs weekend: number of trips and average fare (fare_amount, 2 decimals).
--     Output: day_type ('weekday' or 'weekend'), trips, avg_fare
--     Answer: weekday 2056181 18.62 | weekend 698689 17.83



-- R4. Tips by payment type: trips, and total tips as a percent of total fares (1 decimal).
--     Output: payment_name, trips, tip_pct      (sorted by trips, most first)
--     Answer: Credit Card 2298404 22.6 | Cash 422939 0.0 | Dispute 22879 0.0 | No Charge 10648 0.0
--     (Why is cash 0? Write one sentence about it under your query.)



-- R5. For each borough, the pickup zone with the most trips (tie -> alphabetical zone_name).
--     Output: borough, zone_name, trips      (sorted by trips, most first)
--     Answer (first 3 rows): Queens, JFK Airport, 138130 | Manhattan, Upper East Side South, 137092 | Unknown, N/A, 9480


