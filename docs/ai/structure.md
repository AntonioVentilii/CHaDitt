# Structure

A flat Flask app: four modules at the root and one package. Gunicorn loads `app:app`.

```
app.py                 Flask app and routes; nothing else
configs.py             WhatsApp settings from the environment (GRAPH_API_TOKEN, MOBILE_ID, DEBUG_CHAT_IDS)
message_processor.py   MessageProcessor: webhook routing, WhatsApp replies, in-memory state, log lines,
                       and the pure helpers they use (split_text, parse_reply_id, ...)
translations.py        user-facing strings per language, language labels, calling code to language
openai_wrapper/
  models.py            the OpenAI model names and settings
  prompts.py           long prompts (transcription hint, language detection)
  audio.py             speech_to_text
  chat.py              simple_query and the three text actions (correct, summarize, translate)
  language.py          get_intended_language_iso
scripts/               shell scripts for Heroku testing mode and ngrok, run from inside scripts/
```

## Direction of imports

```
app.py ─▶ message_processor.py ─▶ configs.py
                               ├─▶ translations.py
                               └─▶ openai_wrapper.{audio,chat,language} ─▶ openai_wrapper.{models,prompts}
```

- `translations.py` and `configs.py` import nothing from the project.
- `openai_wrapper/` knows nothing about WhatsApp or `translations.py`: it takes text and plain
  language names and returns text. Keep it that way, so it can be reused or tested alone.
- `app.py` only wires HTTP to `MessageProcessor`; message logic never goes in a route.
- WhatsApp calls go through the `whatsapp-wrapper` package (`self.wa` on `MessageProcessor`), never
  through `requests` directly.

## Where new code goes

| New code                                           | Goes in                                                        |
| -------------------------------------------------- | -------------------------------------------------------------- |
| a string a user reads                              | `translations.py`, a key in every language                     |
| a call to OpenAI, or a prompt                      | `openai_wrapper/` (short prompts inline in `chat.py`, long ones in `prompts.py`) |
| a model name or model setting                      | `openai_wrapper/models.py`                                     |
| an environment variable for WhatsApp               | `configs.py`, and `.env.template`                              |
| a new kind of incoming message, or a new button    | `MessageProcessor` in `message_processor.py` (see `workflows/`) |
| a pure helper on text or ids                       | a module-level function in `message_processor.py`, beside its siblings |
| an HTTP route                                      | `app.py`                                                       |

`message_processor.py` is already the largest file (about 400 lines). A change that would push it
much further should first split it, in its own pull request (ask first: it adds modules). The split
the code suggests: the pure helpers, the WhatsApp message builders, and the processor itself.
