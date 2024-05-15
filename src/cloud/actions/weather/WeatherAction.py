import vertexai
from vertexai.generative_models import (
    Content,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

from src.cloud.actions.BaseAction import BaseAction
from src.cloud.external.WeatherApi import WeatherApi

from abc import ABC


class WeatherAction(BaseAction, ABC):
    
    WEATHER_PARAM_NAME = "weather"
    BASE_URL = "http://dataservice.accuweather.com"
    API_KEY = "cveAxjGo1fpAYcd64xglPwlCqhCgqkjo"
    LOCATION_KEY = '304465'
    
    def __init__(self):
        super().__init__()
        self.weather_api = WeatherApi(base_url=self.BASE_URL, api_key=self.API_KEY)

    def handle(self, parameters: dict):
        print("WeatherAction")
        #assert self.WEATHER_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.WEATHER_PARAM_NAME)
        
        current_conditions = self.weather_api.get_current_conditions(self.LOCATION_KEY)
        forecast = self.weather_api.get_forecast(self.LOCATION_KEY)

        # Construct response
        response = {
            "current_conditions": current_conditions,
            "forecast": forecast
        }

        return super().response_json('weather', response)
    

