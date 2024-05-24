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
    OPTION_PARAM_NAME = "option"

    BASE_URL = "http://dataservice.accuweather.com"
    API_KEY = "cveAxjGo1fpAYcd64xglPwlCqhCgqkjo"
    LOCATION_KEY = '304465'
    
    def __init__(self):
        super().__init__()
        self.weather_api = WeatherApi(base_url=self.BASE_URL, api_key=self.API_KEY)

    def handle(self, parameters: dict):
        print("WeatherAction")
        assert self.OPTION_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.OPTION_PARAM_NAME)

        response = self.weather_api.get_forecast(self.LOCATION_KEY, parameters[self.OPTION_PARAM_NAME])
        return super().response_json('weather', response)
    

