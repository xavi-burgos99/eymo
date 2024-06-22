import re
from vertexai.generative_models import (
    GenerativeModel,
)

from src.cloud.actions.BaseAction import BaseAction
from src.cloud.external.WeatherApi import WeatherApi, farenheit_to_celsius

from abc import ABC
from src.cloud.external.TextToSpeech import text_to_speech

class WeatherAction(BaseAction, ABC):
    OPTION_PARAM_NAME = "option"
    LAT_PARAM_NAME = "latitude"
    LON_PARAM_NAME = "longitude"

    BASE_URL = "http://dataservice.accuweather.com"
    API_KEY = "cveAxjGo1fpAYcd64xglPwlCqhCgqkjo"
    # API_KEY = "FaZJ0i1v5wePcQP37bGk9SxkA8eSIyKM" Yeray
    
    def __init__(self):
        super().__init__()
        self.weather_api = WeatherApi(base_url=self.BASE_URL, api_key=self.API_KEY)

    def handle(self, parameters: dict):
        print("WeatherAction")
        assert self.OPTION_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.OPTION_PARAM_NAME)
        assert self.LAT_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.LAT_PARAM_NAME)
        assert self.LON_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.LON_PARAM_NAME)
        response = self.weather_api.get_forecast(parameters[self.OPTION_PARAM_NAME], parameters[self.LAT_PARAM_NAME], parameters[self.LON_PARAM_NAME])
        min = farenheit_to_celsius(float(response.get("Temperature").get("Minimum").get("Value")))
        max = farenheit_to_celsius(float(response.get("Temperature").get("Maximum").get("Value")))
        print(str(parameters[self.OPTION_PARAM_NAME]))
        prompt = "Datos del tiempo:" + str(parameters[self.OPTION_PARAM_NAME]) + str(response.get("Day").get("IconPhrase")) + \
            "Temperatura minima: " + min + ", temperatura maxima: " +max + " grados Celsius."

        model = GenerativeModel(
            "gemini-pro",
            system_instruction=[
                "Eres un asistente de voz llamado EYMO, diseñado para ayudar.",
                "Siempre debes responder en Español y sin usar onomatopeyas como Ugh, Uff, ni nada similar.",
                "Al darte informacion sobre el clima/tiempo, debes dar una respuesta breve sobre la informacion proporcionada.",
                "Debes resonder de manera graciosa pero siendo preciso, sin mentir."
            ],
        )
        result = model.generate_content(prompt)

        clean_text = result.text.replace('\n', '')
        clean_text = re.sub(r'[^a-zA-Z0-9,.:;-_~=¿?¡!áéíóúÁÉÍÓÚüÜÑñ\s]', '', clean_text)
        text_response = clean_text.strip()
        print(text_response)
        result_base64 = text_to_speech(text_response)
        return super().response_json('weather', result_base64)

        