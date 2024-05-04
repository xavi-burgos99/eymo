import time
import re
import json

import pyttsx3 as tts
import speech_recognition as sr

import threading
import logging

from rpi.services.server_communication import ServerCommunication


def load_responses(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['responses']


def get_help():
    return "No te quiero ayudar. Me caes mal."


function_mapping = {
    "get_help": get_help
}


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

        self.function_map = function_mapping

    def respond(self, text):
        for key, response in self.responses.items():
            if key in text:
                if response in self.function_map:
                    return self.function_map[response]()
                return response

        logging.info(f"Calling Gemini AI with text: {text}")
        return self.server_comm.call_server("gemini", {"prompt": text})

    def listen(self):
        logging.info("Starting the voice assistant service...")
        threading.Thread(target=self.run_assistant()).start()

    def run_assistant(self):
        logging.info("Voice assistant is running...")
        self.speaker.say("Se ha iniciado el asistente de voz. Di 'Oye EYMO' o 'Hola EYMO' para activar el asistente.")
        self.speaker.runAndWait()

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
            self.speaker.say("Hola Yeray, ¿cómo puedo ayudarte?")
            self.speaker.runAndWait()

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
                self.speaker.say("Adiós Yeray, que tengas un buen día.")
                self.speaker.runAndWait()
                break
            elif text:
                response = self.respond(text)
                if response:
                    self.speaker.say(response)
                    self.speaker.runAndWait()

        logging.error("[ASSITANT ACTIVATED] No action detected. Deactivating assistant...")
