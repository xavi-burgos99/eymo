import vertexai
from datetime import date, datetime
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
    HarmCategory,
    HarmBlockThreshold
)

from abc import ABC

from src.cloud.actions.BaseAction import BaseAction


class FunctionalAction(BaseAction, ABC):
    def __init__(self):
        super().__init__()
        vertexai.init(project='eymo-ai-assistant', location="europe-west9")
        self.model = GenerativeModel(model_name="gemini-1.5-pro-preview-0409")

    def _get_weather_tool(self) -> FunctionDeclaration:
        function_name = "get_weather"
        get_weather_func = FunctionDeclaration(
            name=function_name,
            description="Get the weather of a location for today or tomorrow",
            parameters={
                "type": "object",
                "properties": {
                    "option": {
                        "type": "string",
                        "description": "today/tomorrow"
                    },
                },
                "required": ["option", "latitude", "longitude"]
            },
        )

        return get_weather_func

    def _get_music_control_tool(self) -> FunctionDeclaration:
        function_name = "control_music"
        control_music_func = FunctionDeclaration(
            name=function_name,
            description="Control the music playback on a speaker or assistant device. This function recognizes commands for controlling music playback, such as 'play', 'pause', 'stop', 'next', and 'previous'. Keywords and phrases like 'reproduce', 'pausa', 'para', 'detén la canción', 'siguiente', 'anterior', 'reproducir canción', 'detener la música', etc., should be detected and mapped to the corresponding command.",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Music control command. Valid commands are: 'play', 'pause', 'stop', 'next', 'previous'. Examples of phrases that map to these commands include 'reproduce', 'pausa', 'para la canción', 'detén la música', 'siguiente canción', 'canción anterior'."
                    },
                    "song_name": {
                        "type": "string",
                        "description": "Name and artist of the song to play, to search on the music platform."
                    },
                },
                "required": ["command"]
            }
        )

        return control_music_func

    def _get_reminder_tool(self) -> FunctionDeclaration:
        # Ensure the current date and time are in the correct European format
        current_date = date.today().strftime('%Y-%m-%d')
        current_time = datetime.now().strftime('%H:%M:%S')

        function_name = "set_reminder"
        set_reminder_func = FunctionDeclaration(
            name=function_name,
            description=f"Set a reminder. This function can handle specific times and relative times. Examples of requests include 'recuérdame que tengo que levantarme en 5 minutos', 'recuérdame que me tengo que tomar la pastilla en 20 minutos'. Today is {current_date}. The current time is {current_time} (European 24-hour format).",
            parameters={
                "type": "object",
                "properties": {
                    "reminder": {
                        "type": "string",
                        "description": "Reminder text"
                    },
                    "time": {
                        "type": "string",
                        "format": "time",
                        "description": "Time for the reminder in the format 'HH:MM' or 'HH:MM:SS' (European 24-hour format)"
                    },
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": f"Date for the reminder in the format 'YYYY-MM-DD'. Default is today. Today is {current_date}."
                    }
                },
                "required": ["reminder", "time"]
            }
        )

        return set_reminder_func

    def _get_image_details(self) -> FunctionDeclaration:
        get_image_details_func = FunctionDeclaration(
            name="get_image_details",
            description="Captura y analiza una imagen para identificar y describir cualquier objeto, planta, animal, persona u otra cosa que se esté mostrando. Esta función es activada por prompts que soliciten reconocimiento visual, tales como 'reconoce esto', 'qué es esto', 'qué tengo aquí', 'qué planta es esta', 'qué animal es este', 'quién es esta persona', 'qué ves aquí', 'qué hay en la imagen', 'puedes identificar esto', 'qué es lo que tengo en las manos', 'qué aparece aquí', etc. Cualquier otra pregunta que tenga que ver con algo visual, o que pueda estar a la vista de una camara o foco, tambien debera ir a esta pregunta. Pregunta sobre colores, formas o descripciones de objetos que se puedan ver gracias a una imagen tambien deberian redirigirse a esta funcion, puesto que hara la llamada a Gemini Vision para entenderla.",
            parameters={
                "type": "object",
                "properties": {},
                "required": []
            }
        )

        return get_image_details_func

    def handle(self, parameters: dict):
        assert parameters.get("prompt"), self.parameter_must_be_sent(parameter_name="prompt")

        print(parameters.get("prompt"))
        user_prompt_content = Content(
            role="user",
            parts=[
                Part.from_text(parameters.get("prompt")),
            ],
        )

        print(user_prompt_content)

        tool = Tool(
            function_declarations=[self._get_reminder_tool(), self._get_music_control_tool(), self._get_weather_tool(), self._get_image_details()]
        )

        response = self.model.generate_content(
            user_prompt_content,
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH
            },
            generation_config=GenerationConfig(temperature=0),
            tools=[tool],
        )

        print(response)
        try:
            function_call = response.candidates[0].function_calls[0]
            response = dict()
            response['function_name'] = function_call.name
            response['function_args'] = function_call.args
        except IndexError:
            response = None
        return super().response_json('functional', response)
