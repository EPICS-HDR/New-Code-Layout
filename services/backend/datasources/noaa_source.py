from services.backend.datasources.base import DataSource
class NOAADataSource(DataSource):
    def __init__(self):
        super().__init__("NOAA", "noaa")
        self.location_dict = {
            "Bismarck, ND": ["BIS", "Bismarck"],
            "Grand Forks, ND": ["GFK", "Grand Forks"],
            "Minot, ND": ["MOT", "Minot"],
            "Williston, ND": ["ISN", "Williston"]
        }
