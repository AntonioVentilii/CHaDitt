# Reusability catalog

Everything shared that already exists. Search here before writing a helper, a constant or a string
(rule 4 of the standard), and add a line here when you add one.

## Helpers in `message_processor.py`

| Name                         | Line | What it does                                                                 |
| ---------------------------- | ---- | ---------------------------------------------------------------------------- |
| `masked(sender)`             | 38   | Last four digits of a WhatsApp id, for logs                                  |
| `short_id(message_id)`       | 43   | Last eight characters of a message id, for logs                              |
| `raise_with_meta_error`      | 47   | `WhatsAppAPI` error handler that keeps Meta's answer                         |
| `log_outcome(kind, ...)`     | 52   | The one log line per outcome, with elapsed time                              |
| `log_statuses(statuses)`     | 57   | One log line per delivery status, with Meta's error codes                    |
| `describe(e)`                | 63   | `Type: message` of an exception, for logs                                    |
| `split_text(text, limit)`    | 67   | Cuts a text into WhatsApp-sized pieces at a line break or a space            |
| `parse_reply_id(reply_id)`   | 83   | `(action, target language, media id)` of a button or menu row id             |
| `translation_languages(iso)` | 92   | Language name to translate into, and the fallback when already in it         |
| `run_action(action, text, target)` | 99 | Dispatches an action name to its OpenAI function                         |
| `action_from_typed_choice(text)` | 109 | `1`, `2`, `3` typed in reply to a transcription, as an action            |

## `MessageProcessor` methods

| Method                                  | Line | What it does                                                    |
| --------------------------------------- | ---- | --------------------------------------------------------------- |
| `get_/set_user_language`                | 124  | A sender's language, defaulting to the one of their number      |
| `get_/set_user_transcription`           | 130  | A transcription by the id of a message that shows it            |
| `send_reaction`, `mark_as_read`         | 139  | Best-effort side calls                                          |
| `send_text(to, text, reply_to)`         | 151  | Text reply, split and chained when long; returns the ids        |
| `send_buttons(...)`                     | 161  | Body with one reply button per action                           |
| `send_language_menu(...)`               | 177  | List of languages to translate into                             |
| `send_transcription(...)`               | 196  | Transcription with buttons, split when longer than a button body |
| `transcribe(media_id, progress)`        | 283  | Download, convert to mp3, transcribe; records the stage reached |
| `debug_prefix(text, debug)`             | 250  | Marks replies on the test route                                 |
| `send_failure(...)`                     | 389  | Best-effort "something went wrong" in the sender's language     |

## Constants

| Name                                         | Where                                  | Meaning                                   |
| -------------------------------------------- | -------------------------------------- | ----------------------------------------- |
| `PROCESSING_`, `WORKING_`, `DONE_`, `FAILED_REACTION` | `message_processor.py:14`     | The progress emojis                       |
| `BUTTONS_BODY_MAX_CHARS`, `BUTTON_TITLE_MAX_CHARS`, `LIST_ROW_TITLE_MAX_CHARS`, `TEXT_BODY_MAX_CHARS` | `message_processor.py:21` | WhatsApp limits |
| `META_ERROR_BODY_MAX_CHARS`                  | `message_processor.py:19`              | How much of Meta's error to keep          |
| `FALLBACK_TRANSLATION_LANGUAGE`              | `message_processor.py:27`              | Target when the text is already in the default language |
| `ACTIONS`                                    | `message_processor.py:35`              | The reply buttons, in order               |
| `DEFAULT_LANGUAGE`                           | `translations.py:132`                  | `it`                                      |
| `LANGUAGE_LABELS`                            | `translations.py:137`                  | How each language names itself, with a flag |
| `COUNTRY_CALLING_CODE_LANGUAGES`             | `translations.py:151`                  | Calling code to language                  |
| `TRANSCRIPTION_MODEL`, `CHAT_MODEL`, `CHAT_REASONING_EFFORT` | `openai_wrapper/models.py:6` | OpenAI settings                  |
| `ISO_CODE_LENGTH`                            | `openai_wrapper/language.py:4`         | Length of an ISO 639-1 code               |
| `GRAPH_API_TOKEN`, `MOBILE_ID`, `DEBUG_CHAT_IDS` | `configs.py:7`                     | WhatsApp settings                         |
| `IS_TESTING`, `LOCAL_DEV_URL`, `WEBHOOK_VERIFY_TOKEN` | `app.py:14`                   | Webhook verification and testing mode     |

## Strings and languages (`translations.py`)

- `localized_messages` (line 1): every user-facing string, keyed by language then by message key.
  Keys: `language_name`, `unsupported_content`, `changed_language`, `language_not_supported`,
  `header`, `actions_prompt`, `<action>_button`, `<action>_header`, `translate_menu_prompt`,
  `translate_menu_button`, `translate_menu_section`, `choice_not_recognized`, `context_not_found`,
  `action_failed`.
- `get_localized_message(iso, key, **kwargs)` (line 181): a string in a language, falling back to
  the default language; raises on an unknown key.
- `language_for_wa_id(wa_id)` (line 173): a sender's language from the longest matching calling code.
- `check_supported_language(iso, language)` (line 189): whether a requested language is supported,
  with the reply to send.

## OpenAI (`openai_wrapper/`)

| Function                                         | What it does                                     |
| ------------------------------------------------ | ------------------------------------------------ |
| `speech_to_text(path)` (`audio.py:7`)            | Transcribes an audio file                        |
| `simple_query(prompt, text, max_tokens)` (`chat.py:8`) | One system prompt plus the text, returns the answer |
| `correct_text`, `summarize_text`, `translate_text` (`chat.py:23`) | The three actions             |
| `get_intended_language_iso(text)` (`language.py:7`) | The ISO code of the language a text asks for  |

## From `whatsapp-wrapper`

`WhatsAppAPI` (send text, reaction, mark as read, get media, `banned_users`), `MessageObject`
(the base of every outgoing message) and `audio_utilities.convert_audio_to_mp3` (ffmpeg). The
package is Antonio's (AntonioVentilii/whatsapp-wrapper): a missing WhatsApp feature is added there
and released, not reimplemented here.
