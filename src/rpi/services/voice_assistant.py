import time
import re
import json
import threading
import logging

import speech_recognition as sr

from datetime import datetime

from services.server_communication import ServerCommunication
from services.models.audio_player import AudioPlayer
from services.models.speaker import Speaker

from rpi.controllers.camera_controller import CameraController
from rpi.services.models.location import Location


def load_responses(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['responses']


class VoiceAssistant:
    def __init__(self, config: dict, server_communication: ServerCommunication, camera_controller: CameraController = None):
        self.recognizer = sr.Recognizer()
        self.server_comm = server_communication
        self.camera_controller = camera_controller

        self.location = Location()

        self.speaker = Speaker()

        self.responses = json.load(open('./static/intents.json'))["responses"]

        self.pattern = config["pattern"]
        self.threshold_duration = config["threshold_duration"]

        self.timeout = config.get("listen_timeout")
        self.activated_timeout = config["activated_timeout"]

        self.function_map = {
            "get_help": self.get_help,
            "set_reminder": self.set_reminder,
            "get_image_details": self.get_image_details,
        }

        self.player = AudioPlayer()
        self.reminders = []

        reminder_thread = threading.Thread(target=self.check_reminders)
        reminder_thread.start()

    def speak(self, text):
        if self.player and self.player.is_playing:
            self.player.set_volume(40)
            time.sleep(1)
            audio_length = self.speaker.play(text)
            time.sleep(audio_length)
            self.player.set_volume(100)
        else:
            self.speaker.play(text)

    def get_help(self, args):
        return self.server_comm.call_server("speech", {
                            "text": "No te quiero ayudar. Me caes mal."
        }).get("response").get("result")

    def check_reminders(self):
        while True:
            now = datetime.now()
            current_date = now.date()
            current_time = now.time()

            for reminder in self.reminders:
                if reminder.get('date') == current_date:
                    logging.info(f"Reminder: {reminder.get('reminder')} is due today but at {reminder.get('time')}, now it's {current_time}.")
                    if reminder.get('time') <= current_time:
                        logging.info(f"Reminder: {reminder['reminder']} is due now!")
                        reminder_info = reminder.get("reminder")
                        self.speak(self.server_comm.call_server("speech", {
                            "text": f"Te recuerdo que {reminder_info}, mas te vale recordarlo.",
                        }).get("response").get("result"))
                        self.reminders.remove(reminder)
                    continue
                logging.info(f"Reminder: {reminder.get('reminder')} is not due yet on today.")
            time.sleep(30)

    def set_reminder(self, args):
        reminder = args.get('reminder')

        date = datetime.today().date()
        try:
            date = datetime.strptime(args.get('date'), '%Y-%m-%d').date()
        except Exception:
            logging.warning("Invalid date format. Please use YYYY-MM-DD.")

        time = datetime.now().time()
        try:
            time = datetime.strptime(args.get('time'), '%H:%M').time()
        except Exception:
            logging.warning("Invalid time format. Please use HH:MM:SS.")
        logging.info(f"Reminder: {reminder} at {date} {time}")
        self.reminders.append({'reminder': reminder, 'date': date, 'time': time})
        logging.info(f"Recordatorio añadido: '{reminder}' para {date} a las {time}")
        return self.server_comm.call_server("gemini", {
            "prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que le recuerdes al usuario que tiene que hacer {reminder}, el lo tiene que hacer. Responde de acuerdo con esto, un poco indignado porque estas harto de trabajar como un esclavo.",
            "reset": True}).get("response").get("result")

    def play_song(self, args):
        song_name = args
        response = self.server_comm.call_server("music", {"song_name": song_name}).get("response")
        song_url = response.get('result')
        logging.info(f"Song URL: {song_url}")
        self.player.add_to_playlist(song_url)
        logging.info("Starting audio player...")
        if not self.player.is_playing:
            logging.info("Playing the song...")
            self.player.play()
            return self.server_comm.call_server("speech", {
                "prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que pongas la cancion {song_name}. Responde de acuerdo con esto, un poco indignado porque no te gusta nada esa cancion.",
                "reset": True}).get("response").get("result")
        return self.server_comm.call_server("speech", {
            "text": f"De acuerdo, la agrego a la lista de reproduccion.",
        }).get("response").get("result")

    def control_music(self, args):
        command = args.get('command')
        if command == "pause":
            if self.speaker.is_playing:
                self.speaker.stop()
            if self.player and (self.player.is_playing or self.player.paused):
                logging.info("[CONTROL_MUSIC] Pausing the player...")
                self.player.pause()
                return self.server_comm.call_server("speech", {
                    "text": "Vale",
                }).get("response").get("result")
        elif command == "play":
            if args.get('song_name'):
                return self.play_song(args.get('song_name'))
            elif self.player:
                logging.info("[CONTROL_MUSIC] Resuming the player...")
                self.player.play()
                return self.server_comm.call_server("speech", {
                    "text": "Vale, la reanudo.",
                }).get("response").get("result")
        elif command == "stop":
            if self.speaker.is_playing:
                self.speaker.stop()
            if self.player:
                logging.info("[CONTROL_MUSIC] Stopping the player...")
                self.player.stop()
                return self.server_comm.call_server("speech", {
                    "text": "Vale, la detengo.",
                }).get("response").get("result")
            self.speaker.update_playing_status()
        elif command == "next":
            if self.player:
                logging.info("[CONTROL_MUSIC] Playing the next song...")
                self.player.next()
                return self.server_comm.call_server("speech", {
                    "text": "Listo, pongo la siguiente cancion.",
                }).get("response").get("result")
        else:
            logging.warning("[CONTROL_MUSIC] Invalid command.")
            return self.server_comm.call_server("speech", {
                    "text": "No se ha podido controlar la música. Por favor, intenta de nuevo.",
                }).get("response").get("result")

    def get_image_details(self, prompt: str):
        return self.server_comm.call_server("gemini", {
            "prompt": prompt,
            "image": self.camera_controller.get_frame(),
            "reset": False}).get("response").get("result")

    def get_weather(self, args):
        logging.info("Getting weather...")
        data = {
            "option": args.get("option"),
            "latitude": args.get("latitude"),
            "longitude": args.get("longitude"),
        }
        logging.info("Calling weather service...")
        try:
            return (self.server_comm.call_server("weather", data)
                    .get("response")
                    .get("result"))
        except Exception as e:
            logging.error(f"Error calling weather service: {e}")
        return self.server_comm.call_server("speech", {
            "text": "Ha habido un problema al obtener el clima. Por favor, intenta de nuevo.",
        }).get("response").get("result")

    def respond(self, text):
        # Step 1: Check for functional commands
        logging.info("Handling playback...")
        location_data = self.location.get_location()
        response = self.server_comm.call_server("functional", {"prompt": text + " | lat: " + location_data.get("lat") + " lon: " + location_data.get("lon")})
        logging.info(f"Playback response: {response}")
        result = response.get('response').get('result')
        logging.info(f"Playback result: {result}")
        if result:
            if result.get('function_name') == 'control_music':
                return self.control_music(result.get('function_args'))
            elif result.get('function_name') == 'set_reminder':
                return self.set_reminder(result.get('function_args'))
            elif result.get('function_name') == 'get_weather':
                return self.get_weather(result.get('function_args'))

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
            response = self.server_comm.call_server("gemini", {"prompt": text}).get("response").get("result")
            logging.info(f"Response from Gemini AI: {response}")
            return response
        except Exception as e:
            logging.error(f"Error calling Gemini AI: {e}")

        return self.server_comm.call_server("speech", {
                    "text": "Ha habido un problema al procesar tu solicitud. Por favor, intenta de nuevo.",
                }).get("response").get("result")

    def listen(self):
        logging.info("Starting the voice assistant service...")
        threading.Thread(target=self.run_assistant()).start()

    def run_assistant(self):
        logging.info("Voice assistant is running...")

        self.speak(self.server_comm.call_server("gemini", {
            "prompt": "Eres un asistente de voz, llamado EYMO. Te debes presentar a tus usuarios de manera breve y siendo muy cordial."}).get(
            "response").get("result"))

        while True:
            with sr.Microphone(device_index=0) as mic:
                self.recognizer.pause_threshold = 1
                self.recognizer.adjust_for_ambient_noise(mic, duration=self.threshold_duration)
                logging.info("Listening...")
                audio = self.recognizer.listen(mic, None)
                text = self.recognize_speech(audio)
                if text:
                    match = re.match(self.pattern, text, re.IGNORECASE)
                    if match:
                        if self.player.is_playing:
                            self.player.set_volume(40)
                        after_pattern = text[match.end():].strip()
                        logging.info(f"After pattern: {after_pattern}")
                        self.activate_assistant(mic, after_pattern)

    def recognize_speech(self, audio):
        try:
            logging.info("Trying to recognize speech...")
            text = self.recognizer.recognize_google(audio, language="es-ES")
            logging.info(f"Speech recognized: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return None

    def activate_assistant(self, mic, after_pattern=None):
        logging.info("[ASSISTANT ACTIVATED] Keyword detected. Activating assistant.")
        if not after_pattern:
            self.speak(self.server_comm.call_server("gemini", {
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
                audio = self.recognizer.listen(mic, timeout=self.timeout)
                text = self.recognize_speech(audio)

            if text == "para" or text == "adiós":
                logging.info("[ASSISTANT ACTIVATED] Deactivating assistant...")
                if self.player.is_playing:
                    self.player.stop()
                break
            elif text:
                logging.info(f"[ASSISTANT ACTIVATED] Text detected: {text}")
                if self.player.is_playing:
                    self.player.set_volume(40)
                response = self.respond(text)
                if response:
                    self.speak(response)
        logging.error("[ASSITANT ACTIVATED] No action detected. Deactivating assistant...")
