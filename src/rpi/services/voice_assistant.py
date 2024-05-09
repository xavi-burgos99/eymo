import time
import re
import json

import pyttsx3 as tts
import speech_recognition as sr

import threading
import logging

from services.server_communication import ServerCommunication
from services.models.audio_player import AudioPlayer


player = None

def load_responses(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['responses']


def get_help(args):
    return "No te quiero ayudar. Me caes mal."


def play_song(args):
    song_name, server_comm = args[0], args[1]
    response = server_comm.call_server("music", {"song_name": song_name}).get("response")
    song_url = response.get('result')
    logging.info(f"Song URL: {song_url}")

    logging.info("Creating audio player...")
    player = AudioPlayer(song_url)
    logging.info("Starting audio player...")
    playback_thread = threading.Thread(target=player.play)
    logging.info("Starting playback thread...")
    playback_thread.start()
    logging.info("Playback thread started.")
    return player


reminders = []

def set_reminder(args):
    reminder_info = args[0].strip()
    logging.info(f"Reminder info: {reminder_info}")
    time_to_remind = args[1]  # Define la lógica para extraer la hora/momento desde el texto o proporciona directamente
    logging.info(f"Time to remind: {time_to_remind}")
    reminders.append((reminder_info, time_to_remind))
    logging.info(f"Recordatorio añadido: '{reminder_info}' para {time_to_remind}")
    return f"Recordaré {reminder_info}."

def check_reminders():
    while True:
        current_time = time.time()
        for reminder in reminders:
            info, remind_at = reminder
            if current_time >= remind_at:
                logging.info(f"Recordatorio activado: {info}")
                player.speaker.say(f"Recordatorio: {info}")
                player.speaker.runAndWait()
                reminders.remove(reminder)
        time.sleep(60)

reminder_thread = threading.Thread(target=check_reminders)
reminder_thread.start()


function_mapping = {
    "get_help": get_help,
    "play_song": play_song,
    "set_reminder": set_reminder
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
        global player

        # Verifica si es una solicitud para establecer un recordatorio
        if "recuerda" in text:
            logging.info("Setting a reminder...")
            reminder_text = text.split("recuerda", 1)[1].strip()

            # Implementa aquí la lógica para identificar la hora o momento del recordatorio
            # Ejemplo simplificado: asumiendo el formato "en <X minutos>"
            match = re.search(r'en (\d+) minutos?', reminder_text)
            logging.info(f"Match: {match}")
            if match:
                minutes = int(match.group(1))
                logging.info(f"Setting reminder in {minutes} minutes...")
                remind_at = time.time() + (minutes * 60)
                logging.info(f"Reminder time: {remind_at}") 
                return self.function_map["set_reminder"]([reminder_text, remind_at])
            return "No se ha podido establecer el recordatorio. Por favor, usa el formato 'recuerda en <X minutos>'."

        if "pausa" in text:
            if player:
                logging.info("Pausing the player...")
                player.pause()
                return "Pausando la música."
        elif "continúa" in text or "resume" in text:
            if player:
                logging.info("Resuming the player...")
                player.play()
                return "Reanudando la música."
        elif "para" in text or "detén" in text:
            if player:
                logging.info("Stopping the player...")
                player.stop()
                return "Deteniendo la música."

        for key, response in self.responses.items():
            if key in text:
                if response in self.function_map:
                    result = self.function_map[response]([text.replace(key, ""), self.server_comm])
                    if isinstance(result, AudioPlayer):
                        player = result
                    return "De acuerdo, reproduciendo la canción."
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
