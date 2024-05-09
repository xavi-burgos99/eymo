from abc import ABC

from src.cloud.actions.BaseAction import BaseAction
from src.cloud.external.TextToSpeech import text_to_speech

import re
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession


class GeminiAction(BaseAction, ABC):
    PROMPT_PARAM_NAME = "prompt"
    IMAGE_PARAM_NAME = "image"

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

    def get_chat_response(self, chat: ChatSession, prompt: str, image: str) -> str:
        text_response = ""

        responses = chat.send_message(f"Brevemente y en español: {prompt}", stream=True)
        for chunk in responses:
            clean_text = chunk.text.replace('\n', '')
            clean_text = re.sub(r'[^a-zA-Z0-9,.:;¿?¡!áéíóúÁÉÍÓÚüÜ\s]', ' ', clean_text)
            text_response += clean_text.strip()
        return text_response
    

    def handle(self, parameters: dict):
        assert self.PROMPT_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.PROMPT_PARAM_NAME)

        image = None
        if parameters.get(self.IMAGE_PARAM_NAME):
            image = parameters[self.IMAGE_PARAM_NAME]

        if self.chat is None or parameters['reset']:
            self.chat = self.model.start_chat()  

        result = self.get_chat_response(self.chat, parameters[self.PROMPT_PARAM_NAME], image)
        result_base64 = text_to_speech(result)

        return super().response_json('gemini', result_base64)
    
