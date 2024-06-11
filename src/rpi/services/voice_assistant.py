import logging
import queue
import threading
import time
import re

from rpi.models.audio_player import AudioPlayer
from rpi.models.frame_type import FrameType
from rpi.models.screen_mode import ScreenMode
from rpi.models.speaker import Speaker
from rpi.services.service import Service
import speech_recognition as sr


class VoiceAssistantService(Service):
	DEPENDENCIES = ['screen', 'camera', 'cloud', 'data_manager']

	def init(self):
		"""Initialize the service."""
		self.speaker = Speaker()
		self.player = AudioPlayer()

		self.responses = self._config.get('intents')
		self.pattern = self._config.get("pattern", "^(eymo|eimo|heimo|heymo|hemo|imo|inma|e inma|eima|eimos|oímos)\\b")
		self.threshold_duration = self._config.get("threshold_duration", 0.4)
		self.queue_timeout = self._config.get("queue_timeout", 10)

		self.timeout = self._config.get("listen_timeout", 10)
		self.activated_timeout = self._config.get("activated_timeout", 30)

		self.function_map = {
			"get_help": self.__get_help__,
			"set_reminder": self.__set_reminder__,
			"get_image_details": self.__get_image_details__,
			"tripod_mode": self.__toggle_tripod_mode__,
		}
		self.demo_mode = self._config.get("demo_mode", True)

	def destroy(self):
		"""Destroy the service."""
		pass

	def before(self):
		"""Before the loop. (Before the loop method is called, in the service thread)"""
		self.recognizer = sr.Recognizer()

		self.queue = queue.Queue(maxsize=self._config.get("queue_size", 2))
		self.lock = threading.Lock()
		self.stop_listening = threading.Event()

		if self.demo_mode:
			logging.info("Demo mode is activated. Executing...")
			try:
				self.__demo_mode__()
			except Exception as e:
				logging.error(f"Error in demo mode: {e}")
			# TODO: Actualizar archivo de configuración para que no se ejecute en modo demo

		try:
			self.__speak__(self._services['cloud'].call_server("gemini", {
				"prompt": "Eres un asistente de voz, llamado Eymo. Te debes presentar a tus usuarios de manera breve y siendo muy cordial."}).get(
				"response").get("result"))
		except Exception as e:
			logging.error(f"Error in voice assistant initialization: {e}")

		with sr.Microphone(device_index=0) as mic:
			while True:
				self.recognizer.pause_threshold = 1
				self.recognizer.adjust_for_ambient_noise(mic, duration=self.threshold_duration)
				logging.info("Listening...")
				audio = self.recognizer.listen(mic, None)
				text = self.__recognize_speech__(audio)
				if text:
					match = re.match(self.pattern, text, re.IGNORECASE)
					if match:
						if self.player.is_playing:
							self.player.set_volume(40)
						after_pattern = text[match.end():].strip()
						logging.info(f"After pattern: {after_pattern}")
						self.__activate_assistant__(mic, after_pattern)

	def loop(self):
		"""Service loop."""
		pass

	def __speak__(self, text):
		logging.info(f"[SPEAKER] Speaking: {text}")
		self._services['screen'].mode(ScreenMode.SPEAKING)
		if self.player and self.player.is_playing:
			self.player.set_volume(40)
			time.sleep(1)
			audio_length = self.speaker.play(text)
			time.sleep(audio_length)
			self.player.set_volume(100)
		else:
			audio_lenght = self.speaker.play(text)
			time.sleep(audio_lenght)

		logging.info(f"{self.player.is_playing}")
		if self.player.is_playing and not self.player.paused:
			self._services['screen'].mode(ScreenMode.MUSIC)
		else:
			self._services['screen'].mode(ScreenMode.STANDBY)

	def __recognize_speech__(self, audio):
		try:
			logging.info("Trying to recognize speech...")
			text = self.recognizer.recognize_google(audio, language="es-ES")
			logging.info(f"Speech recognized: {text}")
			return text.lower()
		except sr.UnknownValueError:
			return None

	def __activate_assistant__(self, mic, after_pattern=None):
		# self.screen.mode(ScreenMode.RECOGNIZING)
		logging.info("[ASSISTANT ACTIVATED] Keyword detected. Activating assistant.")
		if not after_pattern:
			self.__speak__(self._services['cloud'].call_server("gemini", {
				"prompt": "Eres un asistente de voz, llamado EYMO. Han dicho tu nombre, rapido reacciona como un buen asistente haria."}).get(
				"response").get("result"))

		end_time = time.time() + self.activated_timeout
		while time.time() < end_time:
			logging.info("[ASSISTANT ACTIVATED] Listening...")

			if after_pattern:
				text = after_pattern
				after_pattern = None
			else:
				self.recognizer.pause_threshold = 1
				self.recognizer.adjust_for_ambient_noise(mic, duration=self.threshold_duration)
				audio = self.recognizer.listen(mic)  # timeout=self.timeout)
				text = self.__recognize_speech__(audio)

			if text == "para" or text == "adiós":
				# self.screen.mode(ScreenMode.STANDBY)
				logging.info("[ASSISTANT ACTIVATED] Deactivating assistant...")
				if self.player.is_playing:
					self.player.stop()
				break
			elif text:
				logging.info(f"[ASSISTANT ACTIVATED] Text detected: {text}")
				if self.player.is_playing:
					self.player.set_volume(40)
				response = self.__respond__(text)
				if response:
					self.__speak__(response)
		# self.screen.mode(ScreenMode.STANDBY)
		logging.error("[ASSITANT ACTIVATED] No action detected. Deactivating assistant...")

	def __demo_mode__(self):
		text = self._services['cloud'].call_server("speech", {
			"text": "Hola, soy Eymo, tu asistente de voz. Estoy aquí para ayudarte con diversas tareas cotidianas. A continuación, te mostraré algunas de mis funcionalidades."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Primero, puedo darte respuestas avanzadas usando Google Gemini. Dejame pensar en un chiste de los buenos."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("gemini", {
			"prompt": "cuentame un chiste de los buenos de humor negro sobre informaticos. Cuenta el chiste directamente."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "También puedo predecirte el tiempo de hoy o mañana. Os lo demostraré."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		location_data = self._services['data_manager'].subscribe('robot_location', lambda key, value: None)
		data = {
			"option": "today",
			"latitude": str(location_data.get("lat")),
			"longitude": str(location_data.get("long")),
		}
		text = self._services['cloud'].call_server("weather", data).get("response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		data = {
			"option": "tomorrow",
			"latitude": str(location_data.get("lat")),
			"longitude": str(location_data.get("long")),
		}
		text = self._services['cloud'].call_server("weather", data).get("response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "¿Necesitas que te recuerde algo? Solo dímelo. Por ejemplo: Recuérdame comprar leche mañana a las 10 de la mañana. Si me lo dices de buen humor, alomejor tienes un poco de suerte y te lo recuerdo."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Finalmente, puedo controlar tu música. Ahora pondré Hey Brother de Avicii."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)
		self.player.set_volume(100)

		self.__play_song__("Hey Brother de Avicii")

		time.sleep(15)
		self.player.set_volume(40)
		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "Mientras hablo puedo bajar el volumen de la musica. De esta manera me puedes escuchar mejor."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length)
		self.player.set_volume(100)
		time.sleep(4)

		self.player.set_volume(40)
		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "¿Quieres pausar la música? Solo di: Oye Eymo, pausa la música."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)
		self.__control_music__({"command": "pause"})

		time.sleep(3)

		text = self._services['cloud'].call_server("speech", {
			"text": "¿Quieres agregar otra canción a tu lista de reproducción? Pongamos Wake me up de Avicii en la lista."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		self.__play_song__("Wake me up de Avicii")

		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "¿Reanudamos la cancion? Venga va."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length)

		self.__control_music__({"command": "play"})
		self.player.set_volume(100)
		time.sleep(6)

		self.player.set_volume(40)
		text = self._services['cloud'].call_server("speech", {
			"text": "Ya me he cansado de esta, pongamos la siguiente de la lista."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		self.__control_music__({"command": "next"})
		self.player.set_volume(100)
		time.sleep(12)

		self.__control_music__({"command": "stop"})
		time.sleep(1)
		text = self._services['cloud'].call_server("speech", {
			"text": "Estas son solo algunas de mis funcionalidades. Estoy aquí para hacer tu vida más fácil y ayudarte en lo que necesites. ¡Gracias por escucharme!"}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Por cierto, se me olvidaba. Tambien puedo reconocer lo que ve mi cámara."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length)

		text = self.__get_image_details__("¿Qué ves AHORA en esta imagen?")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		text = self._services['cloud'].call_server("speech", {
			"text": "Ahora si, muchas gracias! Y aqui acaba esta presentacion. Espero haberos divertido."}).get(
			"response").get("result")
		audio_length = self.speaker.play(text)
		time.sleep(audio_length + 1)

		self.player.clear_playlist()

	def __get_help__(self, params):
		return self._services['cloud'].call_server("speech", {
			"text": "No te quiero ayudar. Me caes mal."
		}).get("response").get("result")

	def __set_reminder__(self, params):
		reminder = self._services['reminders'].set_reminder(params, self.__set_reminder_callback__)
		return self._services['cloud'].call_server("gemini", {
			"prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que le recuerdes al usuario que tiene que hacer {reminder}. Confirma que se lo vas a recordar cuando toque, aunque te de pereza.",
			"reset": True}).get("response").get("result")

	def __set_reminder_callback__(self, reminder_info):
		self.__speak__(self._services['cloud'].call_server("speech", {
			"text": f"Te recuerdo que {reminder_info}, mas te vale recordarlo.",
		}).get("response").get("result"))

	def __get_image_details__(self, prompt: str):
		logging.info("Getting image details...")
		return self._services['cloud'].call_server("gemini", {
			"prompt": prompt,
			"image": self._services['camera'].get_frame(FrameType.BASE64),
			"reset": False}).get("response").get("result")

	def __toggle_tripod_mode__(self, params):
		# TODO: Toggle tripod mode from Voice Assistant.
		logging.warning("Tripod mode is not refactorized yet...")
		pass

	def __play_song__(self, args):
		song_name = args
		response = self._services['cloud'].call_server("music", {"song_name": song_name}).get("response")
		song_url = response.get('result')
		logging.info(f"Song URL: {song_url}")
		self.player.add_to_playlist(song_url)
		logging.info(f"Playlist: {self.player.get_playlist()}")
		logging.info(f"Current inidex: {self.player.current_index}")
		logging.info("Starting audio player...")
		if not self.player.is_playing and not self.player.paused:
			logging.info("Playing the song...")
			self.player.play()
			return self._services['cloud'].call_server("gemini", {
				"prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que pongas la cancion {song_name}. Responde de acuerdo con esto, un poco indignado porque no te gusta nada esa cancion.",
				"reset": True}).get("response").get("result")
		return self._services['cloud'].call_server("speech", {
			"text": f"De acuerdo, la agrego a la lista de reproduccion.",
		}).get("response").get("result")

	def __control_music__(self, args):
		command = args.get('command')
		if command == "pause":
			self._services['screen'].mode(ScreenMode.STANDBY)
			if self.speaker.is_playing:
				self.speaker.stop()
			if self.player and (self.player.is_playing or self.player.paused):
				logging.info("[CONTROL_MUSIC] Pausing the player...")
				self.player.pause()
				logging.info(f"Playlist: {self.player.get_playlist()}")
				logging.info(f"Current inidex: {self.player.current_index}")
				return self._services['cloud'].call_server("speech", {
					"text": "Vale",
				}).get("response").get("result")
		elif command == "play":
			if args.get('song_name'):
				return self.__play_song__(args.get('song_name'))
			elif self.player:
				logging.info("[CONTROL_MUSIC] Resuming the player...")
				self.player.play()
				logging.info(f"Playlist: {self.player.get_playlist()}")
				logging.info(f"Current inidex: {self.player.current_index}")
				return self._services['cloud'].call_server("speech", {
					"text": "Vale, la reanudo.",
				}).get("response").get("result")
		elif command == "stop":
			self._services['screen'].mode(ScreenMode.STANDBY)
			if self.speaker.is_playing:
				self.speaker.stop()
				logging.info(f"Playlist: {self.player.get_playlist()}")
				logging.info(f"Current inidex: {self.player.current_index}")
			if self.player:
				logging.info("[CONTROL_MUSIC] Stopping the player...")
				self.player.stop()
				logging.info(f"Playlist: {self.player.get_playlist()}")
				logging.info(f"Current inidex: {self.player.current_index}")
				return self._services['cloud'].call_server("speech", {
					"text": "Vale, la detengo.",
				}).get("response").get("result")
			self.speaker.update_playing_status()
		elif command == "next":
			if self.player:
				logging.info("[CONTROL_MUSIC] Playing the next song...")
				self.player.next()
				logging.info(f"Playlist: {self.player.get_playlist()}")
				logging.info(f"Current inidex: {self.player.current_index}")
				return self._services['cloud'].call_server("speech", {
					"text": "Listo, pongo la siguiente cancion.",
				}).get("response").get("result")
		else:
			logging.warning("[CONTROL_MUSIC] Invalid command.")
			return self._services['cloud'].call_server("speech", {
				"text": "No se ha podido controlar la música. Por favor, intenta de nuevo.",
			}).get("response").get("result")

	def __get_weather__(self, args):
		logging.info("Getting weather...")
		data = {
			"option": args.get("option"),
			"latitude": args.get("latitude"),
			"longitude": args.get("longitude"),
		}
		logging.info("Calling weather service...")
		try:
			return (self._services['cloud'].call_server("weather", data)
					.get("response")
					.get("result"))
		except Exception as e:
			logging.error(f"Error calling weather service: {e}")
		return self._services['cloud'].call_server("speech", {
			"text": "Ha habido un problema al obtener el clima. Por favor, intenta de nuevo.",
		}).get("response").get("result")

	def __respond__(self, text):
		# Step 1: Check for functional commands
		logging.info("Handling playback...")
		location_data = self._services['data_manager'].subscribe('robot_location', lambda key, value: None)
		response = self._services['cloud'].call_server("functional", {
			"prompt": text + " | lat: " + str(location_data.get("lat")) + " lon: " + str(location_data.get("long"))})
		logging.info(f"Playback response: {response}")
		result = response.get('response').get('result')
		logging.info(f"Playback result: {result}")
		if result:
			if result.get('function_name') == 'control_music':
				return self.__control_music__(result.get('function_args'))
			elif result.get('function_name') == 'set_reminder':
				return self.__set_reminder__(result.get('function_args'))
			elif result.get('function_name') == 'get_weather':
				return self.__get_weather__(result.get('function_args'))

		# Step 2: Check for responses in the intents.json file
		for key, response in self.responses.items():
			if key in text:
				if response in self.function_map:
					result = self.function_map[response](text.replace(key, ""))
					if result:
						return result
				return response

		# Step 3: Call Gemini AI otherwise
		logging.info(f"Calling Gemini AI with text: {text}")
		try:
			response = self._services['cloud'].call_server("gemini", {"prompt": text}).get("response").get("result")
			logging.info(f"Response from Gemini AI: {response}")
			return response
		except Exception as e:
			logging.error(f"Error calling Gemini AI: {e}")

		return self._services['cloud'].call_server("speech", {
			"text": "Ha habido un problema al procesar tu solicitud. Por favor, intenta de nuevo.",
		}).get("response").get("result")
