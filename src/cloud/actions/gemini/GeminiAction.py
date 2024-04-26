from abc import ABC

from src.cloud.actions.BaseAction import BaseAction

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession


class GeminiAction(BaseAction, ABC):
    PROMPT_PARAM_NAME = "prompt"

    def __init__(self):
        super().__init__()
        self.settings = {
            'project_id': 'eymo-ai-assistant',
            'location': 'europe-west9',
            'model': 'gemini-1.5-pro-preview-0409'
        }

        vertexai.init(project=self.settings['project_id'], location=self.settings['location'])
        self.model = GenerativeModel(self.settings['model'])
        self.chat = None

    def get_chat_response(self, chat: ChatSession, prompt: str) -> str:
        text_response = []
        responses = chat.send_message(prompt, stream=True)
        for chunk in responses:
            text_response.append(chunk.text)
        return "".join(text_response)

    def handle(self, parameters: dict):
        assert self.PROMPT_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.PROMPT_PARAM_NAME)

        if self.chat is None or parameters['reset']:
            self.chat = self.model.start_chat()

        return self.get_chat_response(self.chat, parameters[self.PROMPT_PARAM_NAME])
