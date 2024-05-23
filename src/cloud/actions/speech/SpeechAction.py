from abc import ABC

from src.cloud.actions.BaseAction import BaseAction
from src.cloud.external.TextToSpeech import text_to_speech

import re
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Part


class SpeechAction(BaseAction, ABC):
    TEXT_PARAM_NAME = "text"

    def __init__(self):
        super().__init__()

    def handle(self, parameters: dict):
        assert self.TEXT_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.TEXT_PARAM_NAME)

        result_base64 = text_to_speech(self.TEXT_PARAM_NAME)
        return super().response_json('speech', result_base64)
    
