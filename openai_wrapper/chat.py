import json

from openai import OpenAI

client = OpenAI()


def simple_query(prompt: str, text: str) -> str:
    query_prompt = {
        "role": "system",
        "content": prompt
    }
    user_message = {
        "role": "user",
        "content": text
    }
    messages = [query_prompt, user_message]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
    )
    ret = json.loads(response.json())
    answer = ret['choices'][0]['message']['content']

    return answer


def correct_text(text: str) -> str:
    prompt = "Correct the grammar and clarify the meaning of the following text. " \
             "Keep it in the same language as the text and answer with the corrected text only."
    ret = simple_query(prompt, text)
    return ret


def summarize_text(text: str) -> str:
    prompt = "Provide a concise summary of the following text, without losing its meaning and without decorative " \
             "sentences like 'In this essay, I will...' or 'This text is about...'. " \
             "Write the summary in the same language as the text."
    ret = simple_query(prompt, text)
    return ret


def translate_text(text: str, target_language: str) -> str:
    prompt = f"Translate the following text into {target_language}. " \
             "Answer with the translation only, without notes or comments. " \
             f"If the text is already in {target_language}, return it unchanged."
    ret = simple_query(prompt, text)
    return ret
