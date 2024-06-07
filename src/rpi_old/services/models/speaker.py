import base64
import pygame
import tempfile
import os
import sys
import logging
import platform
import pyttsx3
from mutagen.mp3 import MP3
from pydub import AudioSegment

import soundfile as sf
from contextlib import contextmanager


@contextmanager
def suppress_stdout():
	with open(os.devnull, "w") as devnull:
		old_stdout = sys.stdout
		sys.stdout = devnull
		try:
			yield
		finally:
			sys.stdout = old_stdout


class Speaker:
	def __init__(self, config: dict):
		pygame.mixer.init()
		self.pitch = config['pitch']
		self.current_file = None

		self.is_playing = False
		self.paused = False

		self.engine = pyttsx3.init()
		if platform.system() == 'Windows':
			self.engine.setProperty('voice', config['voice_id']['win'])
		self.engine.setProperty('rate', config['rate'])

	def _cleanup(self):
		if self.current_file:
			pygame.mixer.music.stop()
			pygame.mixer.quit()
			os.remove(self.current_file)
			self.current_file = None

	def text2speech(self, text: str) -> str:
		"""
		Convert text to speech using espeak-ng
		"""
		with suppress_stdout():
			audio = self.synthesizer.tts(text)
		with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
			sf.write(temp_file, audio, 22050)
			self.current_file = temp_file.name
		sound = AudioSegment.from_wav(self.current_file)
		new_sample_rate = int(sound.frame_rate * (2.0 ** (self.pitch / 12.0)))
		sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
		sound = sound.set_frame_rate(22050)
		sound.export(self.current_file, format="mp3")
		with open(self.current_file, 'rb') as f:
			audio = f.read()
		os.remove(self.current_file)
		return base64.b64encode(audio).decode()

	def play(self, audio: str, tts: bool = False):
		self._cleanup()  # Cleanup any previous audio

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
