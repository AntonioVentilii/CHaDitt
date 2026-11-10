# Change an OpenAI model or prompt

OpenAI retires models; a retired model makes every call fail with a 404 (PR #12).

## A model

1. Check https://platform.openai.com/docs/deprecations and the pricing page: pick a model that is not
   scheduled to retire soon.
2. Change only [`openai_wrapper/models.py`](../../../openai_wrapper/models.py): the constant and the
   comment above it (price, the model it replaces, its retirement date). No model name anywhere else.
3. If the new model needs a different parameter (reasoning effort, token limit name), change
   `simple_query` in [`openai_wrapper/chat.py`](../../../openai_wrapper/chat.py) or `speech_to_text`
   in [`openai_wrapper/audio.py`](../../../openai_wrapper/audio.py), once.
4. Check with the real key: language detection on a request in two languages, one correction, one
   transcription of a short voice note. Put the results and the prices in the pull request body.

## A prompt

Short prompts sit inline in the function that uses them (`chat.py`); long ones in
[`openai_wrapper/prompts.py`](../../../openai_wrapper/prompts.py). Prompts are in English, ask for the
result only, and keep the text's language unless the action is a translation. Language names reach
the prompt from `language_name` in `translations.py`, never typed again.
