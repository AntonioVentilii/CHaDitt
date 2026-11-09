from openai_wrapper.chat import simple_query
from openai_wrapper.prompts import language_prompt

ISO_CODE_LENGTH = 2


def get_intended_language_iso(text) -> str:
    answer = simple_query(language_prompt, text, max_completion_tokens=5)
    return answer.strip().lower()[:ISO_CODE_LENGTH]
