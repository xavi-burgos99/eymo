from abc import ABC

from src.cloud.actions.BaseAction import BaseAction
from src.cloud.external.MusicPlayer import get_song_audio_url

import re
import vertexai

from vertexai.generative_models import GenerativeModel, ChatSession
from piped_api import PipedClient


class MusicAction(BaseAction, ABC):
    SONG_PARAM_NAME = "song_name"
    YOUTUBE_API_KEY = 'AIzaSyC2oHDoObPeM2Veyc2eE0ay_5FdhqYKyWc'
    VIDEO_ID_PARAM_NAME = "video_id"

    def __init__(self):
        super().__init__()
        self.client = PipedClient()
    

    def handle(self, parameters: dict):
        assert self.SONG_PARAM_NAME in parameters.keys(), super().parameter_must_be_sent(self.SONG_PARAM_NAME)
        result_song = None
        if parameters.get(self.VIDEO_ID_PARAM_NAME):
            result_song = get_song_audio_url(self.client, parameters[self.SONG_PARAM_NAME], self.YOUTUBE_API_KEY, parameters[self.VIDEO_ID_PARAM_NAME])
        else:
            result_song = get_song_audio_url(self.client, parameters[self.SONG_PARAM_NAME], self.YOUTUBE_API_KEY)
        
        return super().response_json('music', result_song)
    
