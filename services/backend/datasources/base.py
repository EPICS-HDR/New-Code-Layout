from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
import os
import requests
from typing import Dict, List, Tuple, Any, Optional, Union


class DataSource(ABC):
    def __init__(self, name, data_type):
        self.name = name
        self.data_type = data_type

    @abstractmethod
    def fetch(self, location = None, dataset = None, start_date = None, end_date = None):
        pass

    @abstractmethod
    def process(self, raw_data = None, location = None, dataset = None):
        """
        Process the raw data into a standardized format.
        Must be implemented by derived classes.
        """
        pass

    def store(self, times = None, values= None, location= None, dataset= None):
        """
        Store the processed data in the sql database.
        """
        from backend.database.sqlclasses import updateDictionary
        updateDictionary(times, values, location, dataset, self.data_type)

    def pull(self, location= None, dataset= None, start_date= None, end_date= None):
        """
        Main method to pull and store data from this source.
        """

        raw_data = self.fetch(location, dataset, start_date, end_date)
        times, values = self.process(raw_data, location, dataset)
        self.store(times, values, location, dataset)
        return times, values

    # @abstractmethod
    # def pull_all(self, start_date, end_date):
    #     pass