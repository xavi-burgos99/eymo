import vertexai
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


class HandleplaybackAction(BaseAction, ABC):
    def __init__(self):
        super().__init__()
        vertexai.init(project='eymo-ai-assistant', location="europe-west9")
        self.model = GenerativeModel(model_name="gemini-1.5-pro-preview-0409")

    def handle(self, parameters: dict):
        assert parameters.get("prompt"), self.parameter_must_be_sent(parameter_name="prompt")

        user_prompt_content = Content(
            role="user",
            parts=[
                Part.from_text(parameters.get("prompt")),
            ],
        )

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
                },
            },
        )

        music_control_tool = Tool(
            function_declarations=[control_music_func],
        )

        response = self.model.generate_content(
            user_prompt_content,
            generation_config=GenerationConfig(temperature=0),
            tools=[music_control_tool],
        )

        try:
            function_call = response.candidates[0].function_calls[0]
            response = dict()
            response['function_name'] = function_call.name
            response['function_args'] = function_call.args
        except IndexError:
            response = None
        return super().response_json('handleplayback', response)
