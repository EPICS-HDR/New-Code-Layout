import json
import glob
unique_stations = {}

# Loading all json files in the directory
json_files = glob.glob("*.json")

TOP_LEFT = (45.945248, -104.045343)
BOTTOM_LEFT = (44.997291, -104.031247)
TOP_RIGHT = (45.942412, -100.286123)
BOTTOM_RIGHT = (44.995300, -100.303070)

def is_within_bounds(lat, lon):
    return (BOTTOM_LEFT[0] <= lat <= TOP_RIGHT[0]) and (
        BOTTOM_RIGHT[1] <= lon <= TOP_LEFT[1]
    )

for file in json_files:
    with open(file, "r") as f:
        data = json.load(f)

        if "features" in data:
            for feature in data["features"]:
                attributes = feature["attributes"]
                station_id = attributes["StationID"]
                latitude = attributes["Latitude"]
                longitude = attributes["Longitude"]

                if station_id not in unique_stations and is_within_bounds(
                    latitude, longitude
                ):
                    unique_stations[station_id] = {
                        "Latitude": latitude,
                        "Longitude": longitude,
                    }

print(json.dumps(unique_stations, indent=4))
