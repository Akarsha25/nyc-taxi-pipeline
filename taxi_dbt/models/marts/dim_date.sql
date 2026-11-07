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