SELECT 
    t.recorded_at,
    t.traffic_volume,
    c.day_name,
    c.holiday_name,
    w.temp AS temp_kelvin,
    w.weather_main,
    w.weather_description
FROM traffic_readings t
JOIN calendar_events c ON t.event_date = c.event_date
JOIN weather_observations w ON t.weather_id = w.weather_id
WHERE t.recorded_at BETWEEN '2012-10-02 09:00:00' AND '2012-10-02 14:00:00'
ORDER BY t.recorded_at ASC;

SELECT 
    c.day_name,
    c.is_weekend,
    COUNT(t.reading_id) AS total_hours_observed,
    ROUND(AVG(t.traffic_volume), 2) AS avg_traffic_volume,
    MAX(t.traffic_volume) AS peak_traffic_volume
FROM traffic_readings t
JOIN calendar_events c ON t.event_date = c.event_date
GROUP BY c.day_name, c.is_weekend
ORDER BY avg_traffic_volume DESC;


SELECT 
    w.weather_main,
    COUNT(t.reading_id) AS observation_count,
    ROUND(AVG(t.traffic_volume), 2) AS avg_traffic_volume,
    ROUND(AVG(w.temp), 2) AS avg_temp_kelvin,
    ROUND(AVG(w.rain_1h), 3) AS avg_rainfall_mm
FROM traffic_readings t
JOIN weather_observations w ON t.weather_id = w.weather_id
GROUP BY w.weather_main
HAVING COUNT(t.reading_id) >= 10
ORDER BY avg_traffic_volume DESC;