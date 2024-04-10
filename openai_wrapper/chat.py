import json

from openai import OpenAI

client = OpenAI()


def process_transcription(text: str) -> (str, str):
    grammar_correction_prompt = {
        "role": "system",
        "content": "Correct the grammar and clarify the meaning of the following text."
    }
    user_message_for_correction = {
        "role": "user",
        "content": text
    }
    correction_messages = [grammar_correction_prompt, user_message_for_correction]

    correction_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=correction_messages,
        temperature=0.7,
    )
    correction_ret = json.loads(correction_response.json())
    corrected_text = correction_ret['choices'][0]['message']['content']

    summarisation_prompt = {
        "role": "system",
        "content": "Provide a concise summary of the following text."
    }
    user_message_for_summary = {
        "role": "user",
        "content": corrected_text
    }
    summary_messages = [summarisation_prompt, user_message_for_summary]

    summary_response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=summary_messages,
        max_tokens=150,
        temperature=0.7,
    )
    summary_return = json.loads(summary_response.json())
    summary = summary_return['choices'][0]['message']['content']

    return corrected_text, summary
