const trafficDb = db.getSiblingDB("interstate_traffic_db");

// QUERY 1: Time-Window Filter 

print("QUERY 1: October 2, 2012 Morning Traffic Window (09:00 - 14:00)");

const q1Results = trafficDb.traffic_records.find(
  {
    recorded_at: {
      $gte: ISODate("2012-10-02T09:00:00Z"),
      $lte: ISODate("2012-10-02T14:00:00Z")
    },
    observed: true
  },
  {
    _id: 0,
    recorded_at: 1,
    traffic_volume: 1,
    "calendar.day_name": 1,
    "calendar.holiday.name": 1,
    "weather.temp_kelvin": 1,
    "weather.main": 1,
    "weather.description": 1
  }
).sort({ recorded_at: 1 });

q1Results.forEach(printjson);

// QUERY 2: Day-of-Week Traffic Volume 

print("QUERY 2: Average Traffic Volume by Day of Week");

const q2Results = trafficDb.traffic_records.aggregate([
  {
    $match: { observed: true }
  },
  {
    $group: {
      _id: {
        day_name: "$calendar.day_name",
        is_weekend: "$calendar.is_weekend"
      },
      total_hours_observed: { $sum: 1 },
      avg_traffic_volume: { $avg: "$traffic_volume" },
      peak_traffic_volume: { $max: "$traffic_volume" }
    }
  },
  {
    $project: {
      _id: 0,
      day_name: "$_id.day_name",
      is_weekend: "$_id.is_weekend",
      total_hours_observed: 1,
      avg_traffic_volume: { $round: ["$avg_traffic_volume", 2] },
      peak_traffic_volume: 1
    }
  },
  {
    $sort: { avg_traffic_volume: -1 }
  }
]);

q2Results.forEach(printjson);

// QUERY 3: Impact of Weather on traffic

print("QUERY 3: Weather Severity vs. Average Highway Traffic");

const q3Results = trafficDb.traffic_records.aggregate([
  {
    $match: { observed: true }
  },
  {
    $group: {
      _id: "$weather.main",
      observation_count: { $sum: 1 },
      avg_traffic_volume: { $avg: "$traffic_volume" },
      avg_temp_kelvin: { $avg: "$weather.temp_kelvin" },
      avg_rainfall_mm: { $avg: "$weather.rain_1h_mm" }
    }
  },
  {
    $match: {
      observation_count: { $gte: 10 }
    }
  },
  {
    $project: {
      _id: 0,
      weather_main: "$_id",
      observation_count: 1,
      avg_traffic_volume: { $round: ["$avg_traffic_volume", 2] },
      avg_temp_kelvin: { $round: ["$avg_temp_kelvin", 2] },
      avg_rainfall_mm: { $round: ["$avg_rainfall_mm", 3] }
    }
  },
  {
    $sort: { avg_traffic_volume: -1 }
  }
]);

q3Results.forEach(printjson);