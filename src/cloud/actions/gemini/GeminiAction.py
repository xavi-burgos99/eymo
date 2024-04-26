from abc import ABC

from src.cloud.actions.BaseAction import BaseAction

import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession


class GeminiAction(BaseAction, ABC):
    def __init__(self):
        self.settings = {
            'project_id': 'eymo-ai-assistant',
            'location': 'europe-west9',
            'model' : 'gemini-1.5-pro-preview-0409'
        }
        
        vertexai.init(project=self.settings['project_id'], location=self.settings['location'])
        self.model = GenerativeModel(self.settings['model'])
        self.chat = None
        '''dict = {
            "action": "gemini",
            "parameters": {
                "prompt": "Why does it appear when it rains?",
                "reset": False
            }
        }'''


    def get_chat_response(self, chat: ChatSession, prompt: str) -> str:
        text_response = []
        responses = chat.send_message(prompt, stream=True)
        for chunk in responses:
            text_response.append(chunk.text)
        return "".join(text_response)


    def handle(self, parameters: dict):
        if self.chat is None or parameters['reset']:
            self.chat = self.model.start_chat()

        return self.get_chat_response(self.chat, parameters['prompt'])
