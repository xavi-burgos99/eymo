from typing import Any, Dict, Optional
from src.cloud.external.BaseApi import BaseApi
import logging

class WeatherApi(BaseApi):
    def __init__(self, base_url: str, api_key: str):
        super().__init__(base_url)
        self.api_key = api_key

    '''def get_current_conditions(self, location_key: str) -> Dict[str, Any]:
        """
        Retrieves the current weather conditions for a given location key.
        """
        endpoint = f"/currentconditions/v1/{location_key}?apikey={self.api_key}"
        response = self.send_request("GET", endpoint)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        return response.json()'''

    def get_forecast(self, location_key: str, option:str ,days: int = 5) -> Dict[str, Any]:
        """
        Retrieves the weather forecast for a given location key for the specified number of days.
        """
        number = 0 if option == "current" else 1
        endpoint = f"/forecasts/v1/daily/{days}day/{location_key}?apikey={self.api_key}"
        response = self.send_request("GET", endpoint)
        response.raise_for_status()  # Raise an exception for non-2xx responses

        return response.json().get("DailyForecasts")[number]
