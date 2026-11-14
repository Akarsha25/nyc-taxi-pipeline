select * from {{ref('stg_trips')}}
where fare_amount < 0
or trip_distance<=0
or trip_minutes <0