import logging
import os
import time
import re
import json

from models.audio_player import AudioPlayer
from models.frame_type import FrameType
from models.screen_mode import ScreenMode
from models.setup import save_config
from models.speaker import Speaker
from services.service import Service
import speech_recognition as sr


class VoiceAssistantService(Service):
	DEPENDENCIES = ['screen', 'camera', 'cloud', 'data_manager']
	LOOP_DELAY = 0.01
	MAX_ERRORS = -1
	ERROR_INTERVAL = 60

	DEFAULT_RESPONSES_FILE = "./static/default_responses.json"

	def init(self):
		"""Initialize the service."""
		self.__responses = self._config.get('intents')
		self.__pattern = self._config.get("pattern",
										  "^(eymo|eimo|heimo|heymo|hemo|imo|inma|e inma|eima|eimos|oímos)\\b")
		self.__threshold_duration = self._config.get("threshold_duration", 0.4)
		self.__queue_timeout = self._config.get("queue_timeout", 10)

		self.__timeout = self._config.get("listen_timeout", 10)
		self.__activated_timeout = self._config.get("activated_timeout", 30)

		self.__function_map = {
			"get_help": self.__get_help,
			"set_reminder": self.__set_reminder,
			"get_image_details": self.__get_image_details,
			"tripod_mode": self.__toggle_tripod_mode,
		}
		self._demo_mode = self._config.get("demo_mode", True)

	def destroy(self):
		"""Destroy the service."""
		pass

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.__speaker = Speaker()
		self.__player = AudioPlayer()
		self.__recognizer = sr.Recognizer()

		if not os.path.exists(self.DEFAULT_RESPONSES_FILE):
			self.__default_responses = None
		else:
			with open(self.DEFAULT_RESPONSES_FILE, 'r', encoding='utf-8') as file:
				self.__default_responses = json.load(file)

		# self.__queue = queue.Queue(maxsize=self._config.get("queue_size", 2))
		# self.__lock = threading.Lock()
		# self.__stop_listening = threading.Event()

		while True:
			if self._services['network'].is_connected():
				break

		if self._demo_mode:
			logging.info("Demo mode is activated. Executing...")
			try:
				self.__demo_mode()
			except Exception as e:
				logging.error(f"Error in demo mode: {e}")
			self._global_config.get('voice_assistant', {})['demo_mode'] = False
			save_config(self._global_config)

		try:
			self.__speak(self._services['cloud'].call_server("gemini", {
				"prompt": "Eres un asistente de voz, llamado Eymo. Te debes presentar a tus usuarios de manera breve y siendo muy cordial.",
				"reset": True}).get(
				"response").get("result"))
		except Exception as e:
			logging.error(f"Error in voice assistant initialization: {e}")

	def loop(self):
		"""Service loop."""
		try:
			if self.__player.is_playing and not self.__player.paused:
				self._services['screen'].mode(ScreenMode.MUSIC)
			elif self._services['screen'].get_mode() == ScreenMode.MUSIC:
				self._services['screen'].mode(ScreenMode.STANDBY)
			with sr.Microphone() as mic:
				self.__recognizer.pause_threshold = 1
				self.__recognizer.adjust_for_ambient_noise(mic, duration=self.__threshold_duration)
				logging.debug("Listening...")
				audio = self.__recognizer.listen(mic, timeout=5)
				text = self.__recognize_speech(audio)
				if text:
					match = re.search(self.__pattern, text, re.IGNORECASE)
					if match:
						if self.__player.is_playing:
							self.__player.set_volume(40)
						after_pattern = text[match.end():].strip()
						logging.debug(f"After pattern: {after_pattern}")
						self.__activate_assistant(mic, after_pattern)
		except sr.WaitTimeoutError as e:
			pass
		except Exception as e:
			self._services['screen'].mode(ScreenMode.STANDBY)
			logging.error(f"Error in voice assistant loop {e}")

	def __speak(self, text):
		logging.info(f"[SPEAKER] Speaking: {text}")
		self._services['screen'].mode(ScreenMode.SPEAKING)
		if self.__player and self.__player.is_playing:
			self.__player.set_volume(40)
			time.sleep(1)
			audio_length = self.__speaker.play(text)
			time.sleep(audio_length)
			self.__player.set_volume(100)
		else:
			audio_lenght = self.__speaker.play(text)
			time.sleep(audio_lenght)

		logging.info(f"{self.__player.is_playing}")
		if self.__player.is_playing and not self.__player.paused:
			self._services['screen'].mode(ScreenMode.MUSIC)
		else:
			self._services['screen'].mode(ScreenMode.STANDBY)

	def __recognize_speech(self, audio):
		try:
			self._services['screen'].mode(ScreenMode.RECOGNIZING)
			logging.debug("Trying to recognize speech...")
			text = self.__recognizer.recognize_google(audio, language="es-ES")
			logging.info(f"Speech recognized: {text}")
			self._services['screen'].mode(ScreenMode.STANDBY)
			return text.lower()
		except sr.UnknownValueError:
			self._services['screen'].mode(ScreenMode.STANDBY)
			return None

	def __activate_assistant(self, mic, after_pattern=None):
		logging.info("[ASSISTANT ACTIVATED] Keyword detected. Activating assistant.")
		if not after_pattern:
			self.__speak(self._services['cloud'].call_server("gemini", {
				"prompt": "Eres un asistente de voz, llamado EYMO. Han dicho tu nombre, rapido reacciona como un buen asistente haria."}).get(
				"response").get("result"))

		end_time = time.time() + self.__activated_timeout
		while time.time() < end_time:
			logging.info("[ASSISTANT ACTIVATED] Listening...")

			if after_pattern:
				text = after_pattern
				after_pattern = None
			else:
				self.__recognizer.pause_threshold = 1
				self.__recognizer.adjust_for_ambient_noise(mic, duration=self.__threshold_duration)
				audio = self.__recognizer.listen(mic, timeout=5)
				text = self.__recognize_speech(audio)

			if text == "para" or text == "adiós":
				# self.screen.mode(ScreenMode.STANDBY)
				logging.info("[ASSISTANT ACTIVATED] Deactivating assistant...")
				if self.__player.is_playing:
					self.__player.stop()
				break
			elif text:
				logging.info(f"[ASSISTANT ACTIVATED] Text detected: {text}")
				if self.__player.is_playing:
					self.__player.set_volume(40)
				response = self.__respond(text)
				if response:
					self.__speak(response)
		# self.screen.mode(ScreenMode.STANDBY)
		logging.error("[ASSITANT ACTIVATED] No action detected. Deactivating assistant...")

	def __demo_mode(self):
		text = self._services['cloud'].call_server("speech", {
			"text": "Hola, soy Eymo, tu asistente de voz. Estoy aquí para ayudarte con diversas tareas cotidianas. A continuación, te mostraré algunas de mis funcionalidades."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Primero, puedo darte respuestas avanzadas usando Google Gemini. Dejame pensar en un chiste de los buenos."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("gemini", {
			"prompt": "cuentame un chiste de los buenos de humor negro sobre informaticos. Cuenta el chiste directamente."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "También puedo predecirte el tiempo de hoy o mañana. Os lo demostraré."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		location_data = self._services['data_manager'].subscribe('robot_location', lambda key, value: None)
		data = {
			"option": "today",
			"latitude": str(location_data.get("lat")),
			"longitude": str(location_data.get("long")),
		}
		text = self._services['cloud'].call_server("weather", data).get("response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		data = {
			"option": "tomorrow",
			"latitude": str(location_data.get("lat")),
			"longitude": str(location_data.get("long")),
		}
		text = self._services['cloud'].call_server("weather", data).get("response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "¿Necesitas que te recuerde algo? Solo dímelo. Por ejemplo: Recuérdame comprar leche mañana a las 10 de la mañana. Si me lo dices de buen humor, alomejor tienes un poco de suerte y te lo recuerdo."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Finalmente, puedo controlar tu música. Ahora pondré Hey Brother de Avicii."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)
		self.__player.set_volume(100)

		self.__play_song("Hey Brother de Avicii")

		time.sleep(15)
		self.__player.set_volume(40)
		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "Mientras hablo puedo bajar el volumen de la musica. De esta manera me puedes escuchar mejor."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length)
		self.__player.set_volume(100)
		time.sleep(4)

		self.__player.set_volume(40)
		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "¿Quieres pausar la música? Solo di: Oye Eymo, pausa la música."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)
		self.__control_music({"command": "pause"})

		time.sleep(3)

		text = self._services['cloud'].call_server("speech", {
			"text": "¿Quieres agregar otra canción a tu lista de reproducción? Pongamos Wake me up de Avicii en la lista."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		self.__play_song("Wake me up de Avicii")

		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "¿Reanudamos la cancion? Venga va."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length)

		self.__control_music({"command": "play"})
		self.__player.set_volume(100)
		time.sleep(6)

		self.__player.set_volume(40)
		text = self._services['cloud'].call_server("speech", {
			"text": "Ya me he cansado de esta, pongamos la siguiente de la lista."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		self.__control_music({"command": "next"})
		self.__player.set_volume(100)
		time.sleep(12)

		self.__control_music({"command": "stop"})
		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "Estas son solo algunas de mis funcionalidades. Estoy aquí para hacer tu vida más fácil y ayudarte en lo que necesites. ¡Gracias por escucharme!"}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Por cierto, se me olvidaba. Tambien puedo reconocer lo que ve mi cámara."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length)

		text = self.__get_image_details("¿Qué ves AHORA en esta imagen?")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Ahora si, muchas gracias! Y aqui acaba esta presentacion. Espero haberos divertido."}).get(
			"response").get("result")
		audio_length = self.__speaker.play(text)
		time.sleep(audio_length + 1)

		self.__player.clear_playlist()

	def __get_help(self, params):
		return self._services['cloud'].call_server("speech", {
			"text": "No te quiero ayudar. Me caes mal."
		}).get("response").get("result")

	def __set_reminder(self, params):
		self._services['screen'].mode(ScreenMode.REMINDER)
		reminder = self._services['reminders'].set_reminder(params, self.__set_reminder_callback)
		return self._services['cloud'].call_server("gemini", {
			"prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que le recuerdes al usuario que tiene que hacer {reminder}. Confirma que se lo vas a recordar cuando toque, aunque te de pereza.",
			"reset": True}).get("response").get("result")

	def __set_reminder_callback(self, reminder_info):
		self.__speak(self._services['cloud'].call_server("speech", {
			"text": f"Te recuerdo que {reminder_info}, mas te vale recordarlo.",
		}).get("response").get("result"))

	def __get_image_details(self, prompt: str):
		logging.info("Getting image details...")
		return self._services['cloud'].call_server("gemini", {
			"prompt": prompt,
			"image": self._services['camera'].get_frame(FrameType.BASE64),
			"reset": False}).get("response").get("result")

	def __toggle_tripod_mode(self, params):
		# TODO: Toggle tripod mode from Voice Assistant.
		logging.warning("Tripod mode is not refactorized yet...")
		pass

	def __play_song(self, args):
		song_name = args
		response = self._services['cloud'].call_server("music", {"song_name": song_name}).get("response")
		song_url = response.get('result')
		logging.info(f"Song URL: {song_url}")
		self.__player.add_to_playlist(song_url)
		logging.info(f"Playlist: {self.__player.get_playlist()}")
		logging.info(f"Current inidex: {self.__player.current_index}")
		logging.info("Starting audio player...")
		if not self.__player.is_playing and not self.__player.paused:
			logging.info("Playing the song...")
			self.__player.play()
			return self._services['cloud'].call_server("gemini", {
				"prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que pongas la cancion {song_name}. Responde de acuerdo con esto, un poco indignado porque no te gusta nada esa cancion.",
				"reset": True}).get("response").get("result")
		return self._services['cloud'].call_server("speech", {
			"text": f"De acuerdo, la agrego a la lista de reproduccion.",
		}).get("response").get("result")

	def __control_music(self, args):
		command = args.get('command')
		if command == "pause":
			self._services['screen'].mode(ScreenMode.STANDBY)
			if self.__speaker.is_playing:
				self.__speaker.stop()
			if self.__player and (self.__player.is_playing or self.__player.paused):
				logging.info("[CONTROL_MUSIC] Pausing the player...")
				self.__player.pause()
				logging.info(f"Playlist: {self.__player.get_playlist()}")
				logging.info(f"Current inidex: {self.__player.current_index}")
				if self.__default_responses:
					self.__default_responses.get('vale')
				return self._services['cloud'].call_server("speech", {
					"text": "Vale",
				}).get("response").get("result")
		elif command == "play":
			if args.get('song_name'):
				return self.__play_song(args.get('song_name'))
			elif self.__player:
				logging.info("[CONTROL_MUSIC] Resuming the player...")
				self.__player.play()
				logging.info(f"Playlist: {self.__player.get_playlist()}")
				logging.info(f"Current inidex: {self.__player.current_index}")
				if self.__default_responses:
					self.__default_responses.get('vale')
				return self._services['cloud'].call_server("speech", {
					"text": "Vale, la reanudo.",
				}).get("response").get("result")
		elif command == "stop":
			self._services['screen'].mode(ScreenMode.STANDBY)
			if self.__speaker.is_playing:
				self.__speaker.stop()
				logging.info(f"Playlist: {self.__player.get_playlist()}")
				logging.info(f"Current inidex: {self.__player.current_index}")
			if self.__player:
				logging.info("[CONTROL_MUSIC] Stopping the player...")
				self.__player.stop()
				logging.info(f"Playlist: {self.__player.get_playlist()}")
				logging.info(f"Current inidex: {self.__player.current_index}")
				if self.__default_responses:
					self.__default_responses.get('vale')
				return self._services['cloud'].call_server("speech", {
					"text": "Vale, la detengo.",
				}).get("response").get("result")
			self.__speaker.update_playing_status()
		elif command == "next":
			if self.__player:
				logging.info("[CONTROL_MUSIC] Playing the next song...")
				self.__player.next()
				logging.info(f"Playlist: {self.__player.get_playlist()}")
				logging.info(f"Current inidex: {self.__player.current_index}")
				if self.__default_responses:
					self.__default_responses.get('vale')
				return self._services['cloud'].call_server("speech", {
					"text": "Listo, pongo la siguiente cancion.",
				}).get("response").get("result")
		else:
			logging.warning("[CONTROL_MUSIC] Invalid command.")
			self._services['screen'].mode(ScreenMode.ERROR)

			if self.__default_responses:
				self.__default_responses.get('music_error')
			return self._services['cloud'].call_server("speech", {
				"text": "No se ha podido controlar la música. Por favor, intenta de nuevo.",
			}).get("response").get("result")

	def __get_weather(self, args):
		logging.info("Getting weather...")

		location_data = self._services['data_manager'].subscribe('robot_location', lambda key, value: None)
		data = {
			"option": args.get("option"),
			"latitude": location_data.get('lat'),
			"longitude": location_data.get('long'),
		}
		logging.info("Calling weather service...")
		try:
			return (self._services['cloud'].call_server("weather", data)
					.get("response")
					.get("result"))
		except Exception as e:
			logging.error(f"Error calling weather service: {e}")

		self._services['screen'].mode(ScreenMode.ERROR)
		if self.__default_responses:
			return self.__default_responses.get('weather_error')
		return self._services['cloud'].call_server("speech", {
			"text": "Ha habido un problema al obtener el clima. Por favor, intenta de nuevo.",
		}).get("response").get("result")

	def __respond(self, text):
		try:
			# Step 1: Check for functional commands
			logging.info("Calling functional...")
			response = self._services['cloud'].call_server("functional", {"prompt": text})
			logging.info(f"Functional response: {response}")
			result = response.get('response').get('result')
			logging.info(f"Functional result: {result}")
			if result:
				if result.get('function_name') == 'control_music':
					return self.__control_music(result.get('function_args'))
				elif result.get('function_name') == 'set_reminder':
					return self.__set_reminder(result.get('function_args'))
				elif result.get('function_name') == 'get_weather':
					return self.__get_weather(result.get('function_args'))
				elif result.get('function_name') == 'get_image_details':
					return self.__get_image_details(prompt=text)

			# Step 2: Check for responses in the intents.json file
			for key, response in self.__responses.items():
				if key in text:
					if response in self.__function_map:
						result = self.__function_map[response](text.replace(key, ""))
						if result:
							return result
					return response

			# Step 3: Call Gemini AI otherwise
			logging.info(f"Calling Gemini AI with text: {text}")
			response = self._services['cloud'].call_server("gemini", {"prompt": text}).get("response").get("result")
			logging.info(f"Response from Gemini AI: {response}")
			return response
		except Exception as e:
			logging.error(f"Error calling Gemini AI: {e}")

		self._services['screen'].mode(ScreenMode.ERROR)
		if self.__default_responses:
			return self.__default_responses.get('error')
		return self._services['cloud'].call_server("speech", {
			"text": "Ha habido un problema al procesar tu solicitud. Por favor, intenta de nuevo.",
		}).get("response").get("result")
