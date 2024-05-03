import time
import tkinter as tk

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

        self.responses = {
            "buenos días": "Buenas, ¿en qué puedo ayudarte?",
            "qué tal": "Bien, esperando a que me preguntes algo para poderte ayudar.",
            "texto": "Se entiende por texto una composición ordenada de signos inscritos en un sistema de escritura, cuya lectura permite recobrar un sentido específico referido por el emisor. La palabra texto proviene del latín textus, que significa tejido o entrelazado, de modo que en el origen mismo de la idea del texto se encuentra su capacidad para contener ideas en un hilo o una secuencia de caracteres.",
            "puto": "Me cago en tu puta vida, cabron! No me insultes que te pego.",
            "ayuda": "get_help",
            "grupo": "Hola, gente de Chilling Tea \uD83E\uDDCB"
        }
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
        self.speaker.say("Se ha iniciado el asistente de voz. Di 'EYMO' para activar el asistente.")
        self.speaker.runAndWait()
        self.speaker.stop()

        while True:
            try:
                with sr.Microphone(device_index=0) as mic:
                    self.recognizer.adjust_for_ambient_noise(mic, duration=0.2)
                    audio = self.recognizer.listen(mic)

                    try:
                        text = self.recognizer.recognize_google(audio, language="es-ES")
                    except sr.UnknownValueError as uve:
                        continue

                    logging.info(f"Speech recognized: {text}")
                    text = text.lower()

                    if "eymo" in text or "eimo" in text or "heimo" in text or "heymo" in text:
                        self.speaker.say("Hola Yeray, ¿cómo puedo ayudarte?")
                        self.speaker.runAndWait()
                        self.speaker.stop()

                        timer = time.time()
                        while timer + 30 > time.time():
                            audio = self.recognizer.listen(mic, timeout=30)
                            try:
                                text = self.recognizer.recognize_google(audio, language="es-ES")
                            except sr.UnknownValueError as uve:
                                continue

                            text = text.lower()
                            logging.info(f"Speech recognized: {text}")

                            if text == "para" or text == "adiós":
                                self.speaker.say("Adiós Yeray, que tengas un buen día.")
                                self.speaker.runAndWait()
                                self.speaker.stop()
                                break
                            else:
                                if text is not None:
                                    response = self.respond(text)
                                    if response is not None:
                                        self.speaker.say(response)
                                        self.speaker.runAndWait()

                        logging.error("Aborted. No action detected.")
            except Exception as e:
                logging.error(f"An error occurred: {e}")
                continue
