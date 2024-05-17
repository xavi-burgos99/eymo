import time
import re
import json

import speech_recognition as sr

import threading
import logging

from services.server_communication import ServerCommunication
from services.models.audio_player import AudioPlayer

from services.models.speaker import Speaker


def load_responses(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['responses']


class VoiceAssistant:
    def __init__(self, config: dict, server_communication: ServerCommunication):
        self.recognizer = sr.Recognizer()
        self.server_comm = server_communication

        self.speaker = Speaker()

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

        self.player = AudioPlayer()
        self.reminders = []

        reminder_thread = threading.Thread(target=self.check_reminders)
        reminder_thread.start()

    def speak(self, text):
        if self.player and self.player.is_playing:
            self.player.pause()
            time.sleep(1)
            audio_length = self.speaker.play(text)
            time.sleep(audio_length)
            self.player.pause()
        else:
            self.speaker.play(text)

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
        return self.server_comm.call_server("gemini", {
            "prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que recuerdes {reminder_info}. Responde de acuerdo con esto, un poco indignado porque estas harto de trabajar como un esclavo.",
            "reset": True}).get("response").get("result")
        # return f"Recordaré {reminder_info}."

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
            return self.server_comm.call_server("gemini", {
                "prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que pongas la cancion {song_name} pero hay una sonando ahora mismo y la has agregado a la lista de reproduccion. Responde de acuerdo con esto, un poco indignado porque no te gusta nada esa cancion.",
                "reset": True}).get("response").get("result")
        # playback_thread = threading.Thread(target=self.player.play)
        # logging.info("Starting playback thread...")
        # playback_thread.start()
        # logging.info("Playback thread started.")
        return self.server_comm.call_server("gemini", {
            "prompt": f"Eres un asistente de voz, llamado EYMO. Te han pedido que pongas la cancion {song_name}. Responde de acuerdo con esto, un poco indignado porque no te gusta nada esa cancion.",
            "reset": True}).get("response").get("result")
        # return f"De acuerdo, reproduciendo la canción {song_name}."

    def control_music(self, args):
        command = args.get('command')

        if command == "pause":
            if self.player:
                logging.info("Pausing the player...")
                self.player.pause()
                return self.server_comm.call_server("gemini", {
                    "prompt": "Eres un asistente de voz, llamado EYMO. Te han pedido que pauses la cancion que estaba sonando. Responde de acuerdo con esto.",
                    "reset": True}).get("response").get("result")
                # return "Pausando la música."
        elif command == "play":
            if self.player:
                logging.info("Resuming the player...")
                self.player.play()
                return self.server_comm.call_server("gemini", {
                    "prompt": "Eres un asistente de voz, llamado EYMO. Te han pedido que reanudes cancion que estaba sonando. Responde de acuerdo con esto.",
                    "reset": True}).get("response").get("result")
                #return "Reanudando la música."
        elif command == "stop":
            if self.player:
                logging.info("Stopping the player...")
                self.player.stop()
                return self.server_comm.call_server("gemini", {
                    "prompt": "Eres un asistente de voz, llamado EYMO. Te han pedido que detengas la cancion que estaba sonando. Responde de acuerdo con esto.",
                    "reset": True}).get("response").get("result")
                # return "Deteniendo la música."
        elif command == "next":
            if self.player:
                logging.info("Playing the next song...")
                self.player.next()
                return self.server_comm.call_server("gemini", {
                    "prompt": "Eres un asistente de voz, llamado EYMO. Te han pedido que reproduzcas la siguiente cancion de la playlist. Responde brevemente de acuerdo con esto.",
                    "reset": True}).get("response").get("result")
                # return "Reproduciendo la siguiente canción."
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
            response = self.server_comm.call_server("functional", {"prompt": text})
            logging.info(f"Playback response: {response}")
            result = response.get('response').get('result')
            logging.info(f"Playback result: {result}")

            if result and result.get('function_name') == 'control_music':
                return self.control_music(result.get('function_args'))
            time.sleep(1)  # To avoid overloading responses

        self.speaker.update_playing_status()
        if self.speaker.is_playing:
            logging.info("Handling playback...")
            response = self.server_comm.call_server("functional", {"prompt": text})
            try:
                logging.info(f"Playback response: {response}")
                result = response.get('response').get('result')
                logging.info(f"Playback result: {result}")

                if result and result.get('function_name') == 'control_music':
                    if result.get('function_args').get('command') == 'stop':
                        self.speaker.stop()
                    return
            except Exception as e:
                logging.error(f"Error handling speaker: {e}")
            time.sleep(1)  # To avoid overloading responses

        for key, response in self.responses.items():
            if key in text:
                if response in self.function_map:
                    result = self.function_map[response](text.replace(key, ""))
                    if result:
                        return result
                return response

        logging.info(f"Calling Gemini AI with text: {text}")
        try:
            response = self.server_comm.call_server("gemini", {"prompt": text}).get("response").get("result")
            logging.info(f"Response from Gemini AI: {response}")
            return response
        except Exception as e:
            logging.error(f"Error calling Gemini AI: {e}")

        # return "Ha habido un problema al intentar procesar tu solicitud. Por favor, intenta de nuevo."
        return self.server_comm.call_server("gemini", {
            "prompt": "Eres un asistente de voz, llamado EYMO. Ha habido un problema al procesar una de las solicitudes que te han hecho, responde de acuerdo con esto.",
            "reset": True}).get("response").get("result")

    def listen(self):
        logging.info("Starting the voice assistant service...")
        threading.Thread(target=self.run_assistant()).start()

    def run_assistant(self):
        logging.info("Voice assistant is running...")

        # Hola Soy Eymo, en que te puedo ayudar?
        self.speak(self.server_comm.call_server("gemini", {
            "prompt": "Eres un asistente de voz, llamado EYMO. Te debes presentar a tus usuarios de manera breve y siendo muy cordial."}).get(
            "response").get("result"))

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
            # Hola, me has llamado? Que necesitas?
            self.speak(
                "//NExAAAAANIAAAAAExBTUUzLjEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExFMAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKYAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVIQhDWh7m//NExKwAAANIAAAAAH4PQZBvgZAwFkv5CzrneRPm+8QHkTJAhjnk09gmnrREZ4iPZMmmxMnsEEI7xEZZMBplAMBpwQIEMsgQhzyaewTT1oj/xEY93bE09aIjO0Rjkyab//NExKwAAANIAAAAAADC7YwghlkCEZd3sE02iHPtiabGQ5MmwOT0EDgPgg5vl58pB9Xm35eIGhA0c0u8SsDgITQw84NP998jW5XM2FzifyKJgbB4BQ2BI39N4ATgMhij//NExKwAAANIAAAAAJEv/IqOMghqb//ikBPgzY6yJkX/3+Q0eyCDmE4aH///zA0K5MEQDFYXPicyI///9TQxuHTilDRk0JGhl8PXBsj//7//4NnBYBAMzIOanCIImREC//NExP8fUpVsAU8wAEDdlfoJ4xAYtEKgDHlDNA3PMaeMVVNOjLphcMomupNMFDEBCxE4HWXYzCK3IqCsULU5TpiLm553ioqOP/7Qgy3kf7/NeQmwpWr8Tf1/LwZtV6Tf//NExNQg0ypIAZygAFI8s8dL2sVdBwaISh0CQoOERvfhE+flKkgiscHFiUPix4gnVAyioiPT4/63MMIGUe81/dxZRnGyeWMCGrBi1dTDOoDh8Z0WEWIOTEppEEJstl9E//NExKMgYpKYAdpAAfnU3rZS////6K7ue//6X//T/v697/dCiEH/+gDicMnjkl+l/+RpI0O3gfNKkGmHKmputY0cywoX5ZASwZI452Rma0MORkf/qtf9vX6nciMoo0yv//NExHQQ8fq4AMQEmNn6v7PpK4HfT44jCZ0O/yLG5QvQSgnRWLxBDkpWAGFTIMGh4xemY1C5PUfllSgzjOZT23aUGCyS4CP8CR9WBwkN5qdu0VG/ljkzYn8N6uU9j6WS//NExIMP+QK0AMvEcLgOG8kznLbURnqmQWHBcUYpUX//3V0azshNb6v+iblqUY+YSYRIYWsPY6OwuwizFaxTczyoZ5FQSdTWeurLG1GWbAAoCYbgRDZ1GZAwIP3T0k98//NExJYf0rqcAM4KuANPO02FWGLEuq44+9s9ALuLQUMEBiZbgQ248BM15NSunm5N/Ncx/dW5TR6j09sbjbpyjMvyCnmS2Hf2mkEGB2HJtPaEGGHEAsCMNJXA1YitB/SQ//NExGkhalKMAOYQuDKNLdRCWM08gfOS6D3sXPEhoqekOlHfNhI99/yl/dRQ8wzzXyB3UYQSBwZeRCeXkAgCFDpv3L4h/vlOxu2RgVDO8cV5w0j2cl54lzJeaor7nnT+//NExDYa0laoAMvEuCw8VZ6f0kreTV8dTtiFudoJggCGRwTa9PrLKJBGpI1TyJJZP5023aY95DvdmlkTHag//vVklf5QfczCwDAY7xFwTuFYAwEE5Im422oiYYgsxFEd//NExB0SaRbAAHpecF3CWUic7Mfhatrp6sbm8335/vNrZgMNW5yiYxqcXSLkJP+hYkkVC/LzNHOwGv7hoq94kj9jfbykIPRJBGLjxGGRuKKJpJpR6qAhFAbBsTBcODaF//NExCYROP64AHpScOy3U4fNh7/+bijywnCqUtYNGJkddPZrcTtmZ323f9H9sCHAi1ZFHqQrcCfsogBNjOZVKqu1Pf5asKhVopDIpXaiz/W7Utrdu/vjUokQcBr+1bb///NExDQROQKoAHpScPKyoTTU/kip2e/W4qWK//sW/UyqHaAirpyg5rlGjSKBJEBGnUlutmtuApIMR44Co1OUoTUuj1N/pc3RSVKrajxVxYGg0HTpL0YKgJ8ikqR//1uB//NExEIQoRKIAHmUcKp8pTOMsMEM4nZqs1o1a8zIiLnyVZNJuIpERxuCqjbD3CkaFZ6cHoVqnm//////YrJB5/0t4FCQeCqfFlliUAsOr/////trCgImAQoGAkqkzOpe//NExFIRgQI0AHpScKjH1SCkzGqwMQYyqxnar7Gq0TG9SDEDSzodERLCYSeVESjx08oCjD2oCuPFgK4sWWM+PR+tKss3/yRFdUxBTUUzLjEwMFVVVVVVVVVVTEFNRTMu//NExF8R2QHsABjGcDEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExGoAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVWLKadksS//NExKwAAANIAAAAAMtwCWW0hIUHYNxHTAmI7xgYHm3wHTYgQx7Ymm0EIz///tEf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qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq//NExKwAAANIAAAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq//NExKwAAANIAAAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")

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
                # Espero haberte sido de ayuda, que tengas un buen dia.
                self.speak(
                    "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bHK3P/T1zog+zXv//7///1LehiIrGOXCkF77ue9jr3UKtDp52qvHoXTAXqM1nrWtd1lafUPqNrHtgpDmQ9lmiSIoqD49jOXZ//NExGwSggKcAHpEmGcscOoZWRWLe8aAKGVqpbq02aVqjG//ImmSJ0idDQaR4ieKu7FB0sWq9T9PoG0QcK1FOcelvqsGlVVipQnHURCko8Ulj5DiQqSJkwyWbdKOxrfe//NExHUSkW6AAGMKlG/39v3ksRJhEBNLIYAsqIgk7/4CFzPInez//VXEpOSSEqqwUrLApYMjE8ArxoahRIYFSwdO5ZWROtCbnFodXcsNCK2s7iKGiw0sRndKzy/p933r//NExH0RWQo4AHpScHCJR4rAQaYHVgsVAYbJDbDyUVCEQjBGAC0FiRQEFBA4LA4GQkLCwuGfwKFBI9AFCQsLCwfGRYWIu//xYWIuULC4ZcoWFXf+LC5lwCCQjMwELkVM//NExIoQgJIIADDGTEFNRTMuMTAwVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExJsRsFWQAEpGJDEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKcAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVGkAEY5I+//NExKwAAANIAAAAAAgC9AcW8bGy+ZnmAJiKaSZ/7XDA8WHACACGh2fuMGCjyoJChswPOYcX3ymOTM3uSy3ekK+7b+nYkIl68zJ0aOagoYXRkYrfcF1hQXJ5o36mK5OR//NExKwAAANIAAAAANJto6TFb7bIGIFyeBcVyhxGJ6XbUTNqIydGRtCiKNQ+SDYFlD00kDajAjNCiM1A3JRjqIGPaN6ByQoY86cjWJIQQPQQ9Q6jG+DAAPVIo8KTeKiX//NExKwAAANIAAAAAP06ozOTU7uNWN1cqbO9d32e5ypcL5klNr2pz1vazIr40EEHKKIFrJk6eXPZspDcM3HT2E3e6tRRadkC9TvsixnvF4Yg9IRass9xlE7PCzdvlpuV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VVVVO36BTEFNRTMu//NExP8beUHYAGMMcDEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExOQYmI3kAEjGTTEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExK8AsAQAAOAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVTEFNRTMu//NExKwAAANIAAAAADEwMFVVVVVVVVVV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ADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqTEFNRTMu//NExKwAAANIAAAAADEwMKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq//NExKwAAANIAAAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq//NExKwAAANIAAAAAKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
                break
            elif text:
                response = self.respond(text)
                if response:
                    self.speak(response)

        logging.error("[ASSITANT ACTIVATED] No action detected. Deactivating assistant...")
