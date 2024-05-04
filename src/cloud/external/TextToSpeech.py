
from google.cloud import texttospeech

def text_to_speech():
    client = texttospeech.TextToSpeechClient()
    input_text = "Es esta la voz de Eymo?. scurt scurt."

    # Set the text input to be synthesized
    synthesis_input = texttospeech.SynthesisInput(text=input_text)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.VoiceSelectionParams(
        language_code="es-ES", name="es-ES-Polyglot-1"
    )

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        pitch=7.6, speaking_rate=1.50,
        effects_profile_id=["small-bluetooth-speaker-class-device"],
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # The response's audio_content is binary.
    with open("output.mp3", "wb") as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "output.mp3"')



  