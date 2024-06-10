from abc import ABC

from src.cloud.actions.BaseAction import BaseAction
from src.cloud.external.TextToSpeech import text_to_speech
from src.cloud.external.ImageTmpToGC import upload_base64_image_to_gcs, delete_blob

import re
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Part


class GeminiAction(BaseAction, ABC):
    PROMPT_PARAM_NAME = "prompt"
    IMAGE_PARAM_NAME = "image"
    
    

    def __init__(self):
        super().__init__()
        self.settings = {
            'project_id': 'eymo-ai-assistant',
            'location': 'europe-west9',
            'model': 'gemini-1.5-pro-preview-0409',
            'bucket_name': "eymo-cloud-bucket",
            'blob_name': "temp/gemini_temporal.jpg"
        }

        vertexai.init(project=self.settings['project_id'], location=self.settings['location'])
        self.model = GenerativeModel(self.settings['model'])
        self.chat = None

    def get_chat_response(self, chat: ChatSession, prompt: str, image: str) -> str:
        text_response = ""
        if image is not None:
            responses = self.model.generate_content([image, prompt])
            delete_blob(self.settings['bucket_name'], self.settings['blob_name'])
            return responses.text
        else:
            responses = chat.send_message(f"Brevemente y en español: {prompt}", stream=True)
            for chunk in responses:
                clean_text = chunk.text.replace('\n', '')
                clean_text = re.sub(r'[^a-zA-Z0-9,.:;¿?¡!áéíóúÁÉÍÓÚüÜ\s]', ' ', clean_text)
                text_response += (str(" ") + clean_text.strip())
            return text_response
    

    def handle(self, parameters: dict):
        assert self.PROMPT_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.PROMPT_PARAM_NAME)

        image = None
        if parameters.get(self.IMAGE_PARAM_NAME):
            image_base64 = parameters[self.IMAGE_PARAM_NAME]
            image_file_uri = upload_base64_image_to_gcs(image_base64, self.settings['bucket_name'], self.settings['blob_name']) #"gs://generativeai-downloads/images/scones.jpg"
            image = Part.from_uri(image_file_uri, mime_type="image/png")

        if self.chat is None or parameters.get('reset'):
            self.chat = self.model.start_chat(response_validation=False)  

        result = self.get_chat_response(self.chat, parameters[self.PROMPT_PARAM_NAME], image)
        print(result)
        result_base64 = text_to_speech(result)

        return super().response_json('gemini', result_base64)
    
