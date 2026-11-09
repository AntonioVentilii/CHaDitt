from openai import OpenAI

from openai_wrapper.models import TRANSCRIPTION_MODEL
from openai_wrapper.prompts import speech_to_text_instructions


def speech_to_text(audio_file_path: str) -> str:
    client = OpenAI()  # reads OPENAI_API_KEY from the environment
    with open(audio_file_path, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=audio_file,
            response_format='text',
            prompt=speech_to_text_instructions,
        )
    return str(transcript)
