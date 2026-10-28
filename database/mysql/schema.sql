CREATE DATABASE IF NOT EXISTS interstate_traffic_db;
USE interstate_traffic_db;

-- Drop tables if they exist.
DROP TABLE IF EXISTS traffic_readings;
DROP TABLE IF EXISTS weather_observations;
DROP TABLE IF EXISTS calendar_events;

-- 1. Calendar
CREATE TABLE calendar_events (
    event_date DATE PRIMARY KEY,
    holiday_name VARCHAR(100) NOT NULL DEFAULT 'None',
    is_holiday BOOLEAN NOT NULL DEFAULT FALSE,
    day_name VARCHAR(15) NOT NULL,
    is_weekend BOOLEAN NOT NULL DEFAULT FALSE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Weather Observations
CREATE TABLE weather_observations (
    weather_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recorded_at DATETIME NOT NULL UNIQUE,
    temp DECIMAL(8,3) NULL,
    rain_1h DECIMAL(10,4) NULL DEFAULT 0.0,
    snow_1h DECIMAL(10,4) NOT NULL DEFAULT 0.0,
    clouds_all INT NOT NULL,
    weather_main VARCHAR(50) NOT NULL,
    weather_description VARCHAR(150) NOT NULL,
    INDEX idx_weather_time (recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Traffic Readings 
CREATE TABLE traffic_readings (
    reading_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    recorded_at DATETIME NOT NULL UNIQUE,
    event_date DATE NOT NULL,
    weather_id BIGINT NOT NULL,
    traffic_volume INT NULL,
    observed BOOLEAN NOT NULL DEFAULT FALSE,

    CONSTRAINT fk_traffic_calendar
        FOREIGN KEY (event_date)
        REFERENCES calendar_events(event_date)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_traffic_weather
        FOREIGN KEY (weather_id)
        REFERENCES weather_observations(weather_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    INDEX idx_traffic_date (event_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;