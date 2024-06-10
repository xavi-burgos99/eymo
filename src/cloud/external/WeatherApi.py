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
    

    def get_geoposition(self, latitude: str, longitude: str) -> Dict[str, Any]:
        """
        Retrieves the location key for a given latitude and longitude.
        """
        
        endpoint = f"/locations/v1/cities/geoposition/search?apikey={self.api_key}&q={latitude}%2C{longitude}"
        response = self.send_request("GET", endpoint)
        response.raise_for_status()
        return response.json().get("Key")


    def get_forecast(self, option:str, latitude:str, longitude:str, days: int = 5) -> Dict[str, Any]:
        """
        Retrieves the weather forecast for a given location key for the specified number of days.
        """
        
        location_key = self.get_geoposition(latitude, longitude)
        number = 0 if option == "today" else 1
        endpoint = f"/forecasts/v1/daily/{days}day/{location_key}?apikey={self.api_key}"
        response = self.send_request("GET", endpoint)
        response.raise_for_status()  # Raise an exception for non-2xx responses

        return response.json().get("DailyForecasts")[number]

def farenheit_to_celsius(farenheit):
        celsius = "{:.2f}".format((farenheit - 32) * 5.0/9.0)
        return str(celsius)