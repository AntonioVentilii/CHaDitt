from openai import OpenAI

from openai_wrapper.prompts import speech_to_text_instructions


def speech_to_text(audio_file_path: str) -> str:
    client = OpenAI()
    # defaults to getting the key using os.environ.get("OPENAI_API_KEY")
    # if you saved the key under a different environment variable name, you can do something like:
    # client = OpenAI(
    #   api_key=os.environ.get("CUSTOM_ENV_NAME"),
    # )
    audio_file = open(audio_file_path, 'rb')
    transcript = client.audio.transcriptions.create(
        model='whisper-1',
        file=audio_file,
        response_format='text',
        temperature=0.8,
        prompt=speech_to_text_instructions
    )
    return str(transcript)


if __name__ == '__main__':
    print(speech_to_text('/Users/av/Downloads/test.mp3'))
