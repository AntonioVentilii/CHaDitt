from openai import OpenAI

from openai_wrapper.models import CHAT_MODEL, CHAT_REASONING_EFFORT

client = OpenAI()


def simple_query(prompt: str, text: str, max_completion_tokens: int = None) -> str:
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": text},
    ]
    extra = {'max_completion_tokens': max_completion_tokens} if max_completion_tokens else {}
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        reasoning_effort=CHAT_REASONING_EFFORT,
        **extra,
    )
    return response.choices[0].message.content.strip()


def correct_text(text: str) -> str:
    prompt = "Correct the grammar and clarify the meaning of the following text, keeping its language. " \
             "Reply with the corrected text only."
    return simple_query(prompt, text)


def summarize_text(text: str) -> str:
    prompt = "Provide a concise summary of the following text, in the same language as the text, without losing " \
             "its meaning and without decorative sentences like 'In this essay, I will...' or 'This text is about...'."
    return simple_query(prompt, text)


def translate_text(text: str, target_language: str, fallback_language: str) -> str:
    prompt = f"Translate the following text into {target_language}. If it is already in {target_language}, " \
             f"translate it into {fallback_language} instead. Reply with the translation only."
    return simple_query(prompt, text)
