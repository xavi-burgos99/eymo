import json


def load_system_configurations() -> dict:
    return {
        "arduino": {

        },
        "screen": {

        },
        "server": {
            "host": "http://localhost:7125",
            "endpoint": "action/perform"
        },
        "voice": {
            "voice_id": "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-ES_HELENA_11.0",
            "rate": 150
        }
    }
