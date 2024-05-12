import time
import re
import json

import pyttsx3 as tts
import speech_recognition as sr

import threading
import logging

from services.server_communication import ServerCommunication
from services.models.audio_player import AudioPlayer


def load_responses(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['responses']


class VoiceAssistant:
    def __init__(self, config: dict, server_communication: ServerCommunication):
        self.recognizer = sr.Recognizer()
        self.server_comm = server_communication

        self.speaker = tts.init()
        self.speaker.setProperty("voice", config["voice_id"])
        self.speaker.setProperty("rate", config["rate"])

        self.responses = json.load(open('./static/intents.json'))["responses"]

        self.pattern = config["pattern"]
        self.threshold_duration = config["threshold_duration"]

        self.timeout = config.get("listen_timeout")
        self.activated_timeout = config["activated_timeout"]

        self.function_map = {
            "get_help": self.get_help,
            "play_song": self.play_song,
            "set_reminder": self.set_reminder
        }

        self.player = None
        self.reminders = []

        reminder_thread = threading.Thread(target=self.check_reminders)
        reminder_thread.start()

    def speak(self, text):
        if self.player and self.player.is_playing:
            self.player.pause()
            time.sleep(1)
            self.speaker.say(text)
            self.speaker.runAndWait()
            time.sleep(1)
            self.player.play()
        else:
            self.speaker.say(text)
            self.speaker.runAndWait()

    def get_help(self, args):
        return "No te quiero ayudar. Me caes mal."

    def check_reminders(self):
        while True:
            current_time = time.time()
            for reminder in self.reminders:
                info, remind_at = reminder
                if current_time >= remind_at:
                    logging.info(f"Recordatorio activado: {info}")

                    # TODO: Implementar la lógica para recordar al usuario sobre el recordatorio por voz
                    # player.speaker.say(f"Recordatorio: {info}")
                    # player.speaker.runAndWait()

                    self.reminders.remove(reminder)
            time.sleep(60)

    def set_reminder(self, args):
        reminder_info = args.get('reminder_text').strip()
        logging.info(f"Reminder info: {reminder_info}")
        time_to_remind = args.get('remind_at')
        logging.info(f"Time to remind: {time_to_remind}")
        self.reminders.append((reminder_info, time_to_remind))
        logging.info(f"Recordatorio añadido: '{reminder_info}' para {time_to_remind}")
        return f"Recordaré {reminder_info}."

    def play_song(self, args):
        song_name = args
        response = self.server_comm.call_server("music", {"song_name": song_name}).get("response")
        song_url = response.get('result')
        logging.info(f"Song URL: {song_url}")

        logging.info("Creating audio player...")
        self.player = AudioPlayer(song_url)
        logging.info("Starting audio player...")
        playback_thread = threading.Thread(target=self.player.play)
        logging.info("Starting playback thread...")
        playback_thread.start()
        logging.info("Playback thread started.")
        return f"De acuerdo, reproduciendo la canción {song_name}."

    def control_music(self, args):
        command = args.get('command')

        if command == "pause":
            if self.player:
                logging.info("Pausing the player...")
                self.player.pause()
                return "Pausando la música."
        elif command == "play":
            if self.player:
                logging.info("Resuming the player...")
                self.player.play()
                return "Reanudando la música."
        elif command == "stop":
            if self.player:
                logging.info("Stopping the player...")
                self.player.stop()
                return "Deteniendo la música."
        else:
            return "No se ha podido controlar la música. Por favor, intenta de nuevo."

    def respond(self, text):
        # TODO: Implementar la lógica para establecer recordatorios segun Gemini AI Functions.
        if "recuerda" in text:
            logging.info("Setting a reminder...")
            reminder_text = text.split("recuerda", 1)[1].strip()
            match = re.search(r'en (\d+) minutos?', reminder_text)
            logging.info(f"Match: {match}")
            if match:
                minutes = int(match.group(1))
                logging.info(f"Setting reminder in {minutes} minutes...")
                remind_at = time.time() + (minutes * 60)
                logging.info(f"Reminder time: {remind_at}")

                request = dict()
                request["reminder_text"] = reminder_text
                request["remind_at"] = remind_at
                return self.function_map["set_reminder"](request)
            return "No se ha podido establecer el recordatorio. Por favor, usa el formato 'recuerda en X minutos'."

        if self.player and (self.player.is_playing or self.player.paused):
            logging.info("Handling playback...")
            response = self.server_comm.call_server("handleplayback", {"prompt": text})
            logging.info(f"Playback response: {response}")
            result = response.get('response').get('result')
            logging.info(f"Playback result: {result}")

            if result and result.get('function_name') == 'control_music':
                return self.control_music(result.get('function_args'))
            time.sleep(1)  # To avoid overloading responses

        for key, response in self.responses.items():
            if key in text:
                if response in self.function_map:
                    result = self.function_map[response](text.replace(key, ""))
                    if result:
                        return result
                return response

        logging.info(f"Calling Gemini AI with text: {text}")
        return self.server_comm.call_server("gemini", {"prompt": text})

    def listen(self):
        logging.info("Starting the voice assistant service...")
        threading.Thread(target=self.run_assistant()).start()

    def run_assistant(self):
        logging.info("Voice assistant is running...")
        self.speak("Hola Yeray, soy EYMO tu asistente de voz. ¿En qué puedo ayudarte?")

        while True:
            with sr.Microphone(device_index=0) as mic:
                self.recognizer.adjust_for_ambient_noise(mic, duration=self.threshold_duration)
                logging.info("Listening...")
                audio = self.recognizer.listen(mic, None)

                text = self.recognize_speech(audio)
                if text:
                    match = re.match(self.pattern, text, re.IGNORECASE)
                    if match:
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
            self.speak("Hola Yeray, ¿cómo puedo ayudarte?")

        end_time = time.time() + self.activated_timeout
        while time.time() < end_time:
            logging.info("[ASSISTANT ACTIVATED] Listening...")

            if after_pattern:
                text = after_pattern
                after_pattern = None
            else:
                self.recognizer.adjust_for_ambient_noise(mic, duration=self.threshold_duration)
                audio = self.recognizer.listen(mic, timeout=self.timeout)
                text = self.recognize_speech(audio)

            if text == "para" or text == "adiós":
                self.speak("Adiós Yeray, que tengas un buen día.")
                break
            elif text:
                response = self.respond(text)
                if response:
                    self.speak(response)

        logging.error("[ASSITANT ACTIVATED] No action detected. Deactivating assistant...")
