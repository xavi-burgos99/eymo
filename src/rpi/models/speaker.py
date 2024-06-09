import base64
import pygame
import tempfile
import os
import logging
from mutagen.mp3 import MP3


class Speaker:
    def __init__(self):
        pygame.mixer.init()
        self.current_file = None

        self.is_playing = False
        self.paused = False

    def _cleanup(self):
        if self.current_file:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            os.remove(self.current_file)
            self.current_file = None

    def play(self, audio: str):
        self._cleanup()

        try:
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                decoded_base64 = base64.b64decode(audio)
                temp_file.write(decoded_base64)
                self.current_file = temp_file.name

            pygame.mixer.init()
            pygame.mixer.music.load(self.current_file)
            pygame.mixer.music.play()
            self.is_playing = True
            self.paused = False
            logging.info("Audio playing")

            # Calculate the length of the audio file
            audio = MP3(self.current_file)
            audio_length = audio.info.length
            logging.info(f"Audio length: {audio_length} seconds")
            return audio_length
        except pygame.error as err:
            logging.error(f'Error occurred: {err}')
            self.is_playing = False
            self.paused = False
            return None
        except Exception as err:
            logging.error(f'Error occurred: {err}')
            self.is_playing = False
            self.paused = False
            return None

    def pause(self):
        """
        If the audio is playing, pause it. If it is paused, resume it.
        """
        if pygame.mixer.music.get_busy():
            if pygame.mixer.music.get_pos() > 0:
                pygame.mixer.music.pause()
                logging.info("Audio paused")
                self.is_playing = False
                self.paused = True
        elif pygame.mixer.music.get_pos() > 0:
            pygame.mixer.music.unpause()
            logging.info("Audio resumed")
            self.is_playing = True
            self.paused = False

    def update_playing_status(self):
        if self.is_playing:
            self.is_playing = pygame.mixer.music.get_busy()

    def stop(self):
        pygame.mixer.music.stop()
        logging.info("Audio stopped")
        self.is_playing = False
        self.paused = False
        self._cleanup()

    def __del__(self):
        self._cleanup()
