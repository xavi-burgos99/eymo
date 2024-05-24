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
from src.cloud.external.TextToSpeech import text_to_speech

class WeatherAction(BaseAction, ABC):
    OPTION_PARAM_NAME = "option"
    LAT_PARAM_NAME = "latitude"
    LON_PARAM_NAME = "longitude"

    BASE_URL = "http://dataservice.accuweather.com"
    API_KEY = "cveAxjGo1fpAYcd64xglPwlCqhCgqkjo"
    LOCATION_KEY = '304465'
    
    def __init__(self):
        super().__init__()
        self.weather_api = WeatherApi(base_url=self.BASE_URL, api_key=self.API_KEY)

    def handle(self, parameters: dict):
        print("WeatherAction")
        assert self.OPTION_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.OPTION_PARAM_NAME)
        assert self.LAT_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.LAT_PARAM_NAME)
        assert self.LON_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.LON_PARAM_NAME)

        response = self.weather_api.get_forecast(parameters[self.OPTION_PARAM_NAME], parameters[self.LAT_PARAM_NAME], parameters[self.LON_PARAM_NAME])
        print(response.get("Day").get("IconPhrase"))
        prompt = f"En español, dame una respuesta que contenga: Description: {response.get("Day").get("IconPhrase")} \
            The temperature will be bettween {response.get("Temperature").get("Minimum").get("Value")} \
            and {response.get("Temperature").get("Maximum").get("Value")} degrees"  
        ##### TODO: return base64 audio with the weather forecast using gemini
        model = GenerativeModel("gemini-pro")
        result = model.generate_content(prompt)
        print(result)
        
        
        result_base64 = text_to_speech(result)
        return super().response_json('weather', result_base64)

        