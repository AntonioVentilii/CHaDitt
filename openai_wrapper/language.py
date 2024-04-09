import json

from openai import OpenAI

from openai_wrapper.prompts import language_prompt


def get_intended_language_iso(text) -> str:
    prompt = language_prompt

    client = OpenAI()

    messages = [
        {
            "role": "system",
            "content": prompt,
        },
        {
            "role": "user",
            "content": text,
        }
    ]

    r = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=3,
        temperature=0.3  # Lower temperature might help in generating more predictable outcomes
    )
    ret = json.loads(r.json())

    iso_language_code = ret['choices'][0]['message']['content'].strip()
    return iso_language_code
