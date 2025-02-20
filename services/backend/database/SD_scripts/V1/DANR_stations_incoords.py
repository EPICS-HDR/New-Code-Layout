import json

# Load station locations from file
with open("new-versions/V1/station_location.json", "r") as file:
    stations = json.load(file)

# Bounding box coordinates
TOP_LEFT = (45.945248, -104.045343)
BOTTOM_LEFT = (44.997291, -104.031247)
TOP_RIGHT = (45.942412, -100.286123)
BOTTOM_RIGHT = (44.995300, -100.303070)

max_lat = max(TOP_LEFT[0], TOP_RIGHT[0], BOTTOM_LEFT[0], BOTTOM_RIGHT[0])
min_lat = min(TOP_LEFT[0], TOP_RIGHT[0], BOTTOM_LEFT[0], BOTTOM_RIGHT[0])
max_long = max(TOP_LEFT[1], TOP_RIGHT[1], BOTTOM_LEFT[1], BOTTOM_RIGHT[1])
min_long = min(TOP_LEFT[1], TOP_RIGHT[1], BOTTOM_LEFT[1], BOTTOM_RIGHT[1])

# Filter stations within the bounding box
filtered_stations = {
    key: value
    for key, value in stations.items()
    if min_lat <= value["Latitude"] <= max_lat
    and min_long <= value["Longitude"] <= max_long
}

print(filtered_stations)
print(json.dumps(filtered_stations, indent=4))
