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

    def fetch(self, location = None, dataset = None, start_date = None, end_date = None):

    def process(self, raw_data = None, location = None, dataset = None):

