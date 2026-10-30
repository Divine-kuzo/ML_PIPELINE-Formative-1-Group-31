from .api_client import fetch_traffic_data

records = fetch_traffic_data(
    start_date="2018-09-28",
    end_date="2018-09-30"
)

print("\nFirst record:")
print(records[0])

print("\nNumber of records:")
print(len(records))