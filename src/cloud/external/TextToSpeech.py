import base64
from google.cloud import texttospeech

def text_to_speech(input_text : str):
    """Synthesizes speech from the input string of text.

    Args:
        input_text (str): Text to be converted to speech

    Returns:
        base64 (str): Base64 encoded audio file
    """

    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    # Characteristic of the voice
    voice = texttospeech.VoiceSelectionParams(language_code="es-ES", name="es-ES-Polyglot-1")

    audio_config = texttospeech.AudioConfig(pitch=7.6, speaking_rate=1.50, effects_profile_id=["small-bluetooth-speaker-class-device"], audio_encoding=texttospeech.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

    return save_audio_base64(response)


def save_audio_base64(response: str) -> str:
    # Encode audio content as base64
    return base64.b64encode(response.audio_content).decode('utf-8')


def save_audio(response: str, file_name: str):
    # The response's audio_content saved to a mp3 file.
    with open(f"{file_name}.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "{}"'.format(file_name))

    