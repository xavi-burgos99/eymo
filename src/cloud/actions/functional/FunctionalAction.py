import vertexai
from datetime import date
from vertexai.generative_models import (
    Content,
    FunctionDeclaration,
    GenerationConfig,
    GenerativeModel,
    Part,
    Tool,
)

from abc import ABC

from src.cloud.actions.BaseAction import BaseAction


class FunctionalAction(BaseAction, ABC):
    def __init__(self):
        super().__init__()
        vertexai.init(project='eymo-ai-assistant', location="europe-west9")
        self.model = GenerativeModel(model_name="gemini-1.5-pro-preview-0409")

    def _get_music_control_tool(self) -> FunctionDeclaration:
        function_name = "control_music"
        control_music_func = FunctionDeclaration(
            name=function_name,
            description="Control the music playback on a speaker or assistant device",
            parameters={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Music control command such as 'play', 'pause', 'stop', 'next', 'previous'"
                    },
                    "song_name": {
                        "type": "string",
                        "description": "Name and artist of the song to play to search on the music platform"
                    },
                },
                "required": ["command"]
            },
        )

        return control_music_func

    def _get_reminder_tool(self) -> FunctionDeclaration:
        function_name = "set_reminder"
        set_reminder_func = FunctionDeclaration(
            name=function_name,
            description="Set a reminder",
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
                        "description": "Time for the reminder in the format 'HH:MM' or 'HH:MM:SS'"
                    },
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "Date for the reminder in the format 'YYYY-MM-DD'. Default is today." + f". Today is {date.today().strftime('%Y-%m-%d')}"
                    }
                },
                "required": ["reminder", "time"]
            },
        )

        return set_reminder_func

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
            function_declarations=[self._get_reminder_tool(), self._get_music_control_tool()],
        )

        response = self.model.generate_content(
            user_prompt_content,
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
