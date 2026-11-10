# Patterns

The patterns the code uses today, with an example of each. Follow them; the anti-patterns at the
end are in the code but must not be copied.

## Handling a webhook

- One entry point, `MessageProcessor.process_webhook_post_request`
  ([`message_processor.py:209`](../../message_processor.py)): it drops other phone numbers, logs
  delivery statuses, drops banned and (on the test route) non-debug senders, marks the message read,
  then dispatches on `message['type']` to one `process_*` method.
- Each `process_*` method reads `recipient_id`, `message_id` and the sender's language at its top,
  starts a timer, and ends in exactly one outcome log line. Example: `process_audio`
  ([`message_processor.py:254`](../../message_processor.py)).
- The route always answers `{'success': True}` when the handler returns. An exception becomes a 500,
  which makes Meta retry: raise only when a retry could help (the transcription), not for side calls.

## Replies

- Every answer is a reply to a message (`reply_to`), so the chat shows what it answers.
- Text goes through `send_text` ([`message_processor.py:151`](../../message_processor.py)), which
  splits at WhatsApp's 4096 characters and chains the pieces as replies.
- Interactive messages (buttons, list) are built from `MessageObject(...).base_data` plus an
  `interactive` dict: `send_buttons` ([`message_processor.py:161`](../../message_processor.py)),
  `send_language_menu` ([`message_processor.py:177`](../../message_processor.py)). Titles are cut to
  the WhatsApp limits with the named constants.
- A button id encodes what is needed to act without memory: `'<action>:<media id>'`, and for a menu
  row `'translate:<iso>:<media id>'`; `parse_reply_id`
  ([`message_processor.py:83`](../../message_processor.py)) reads both.
- Debug replies (the `/test/webhook` route) are prefixed through `debug_prefix`
  ([`message_processor.py:250`](../../message_processor.py)).

## Progress feedback

Reactions on the user's message, never extra text: 👂 while transcribing, ⏳ while a button's action
runs, ✅ when done, ❌ on failure (`*_REACTION` constants,
[`message_processor.py:14`](../../message_processor.py)).

## State

Two dicts on `MessageProcessor` ([`message_processor.py:121`](../../message_processor.py)), read and
written only through `get_/set_user_language` and `get_/set_user_transcription`. Transcriptions are
keyed by the id of every message a reply can point to (the transcription, the buttons, the menu).
When a lookup misses, the voice note is downloaded and transcribed again (`transcribe_again`,
[`message_processor.py:293`](../../message_processor.py)). No database, no files.

## Errors

- Side calls are best effort: `send_reaction`, `mark_as_read`, `send_failure`
  ([`message_processor.py:139`](../../message_processor.py)) catch, print and carry on.
- WhatsApp errors keep Meta's answer through `raise_with_meta_error`
  ([`message_processor.py:47`](../../message_processor.py)).
- A failure in a button's action reacts ❌ and tells the user with `action_failed`, then returns.
- Errors are described for logs with `describe(e)` ([`message_processor.py:63`](../../message_processor.py)).

## Logs

`print`, one line per outcome, through `log_outcome`
([`message_processor.py:52`](../../message_processor.py)):
`[kind] …1234 …abcdef12 outcome 1.2s detail`. The kind is `audio`, `text`, `retranscribe`, an action
name or `status`. A `received` line with no outcome line after it means a hang. Senders go through
`masked`, message ids through `short_id`; message text never reaches the logs. On Heroku the lines
end up in `heroku logs` and the Papertrail add-on.

## OpenAI

- Text actions go through `simple_query` ([`openai_wrapper/chat.py:8`](../../openai_wrapper/chat.py)):
  a system prompt plus the text, with the model and reasoning effort from `models.py`.
- Prompts ask the model to keep the text's language and to reply with the result only.

## Anti-patterns in the code (do not copy)

- `assistant_instructions` in [`openai_wrapper/prompts.py:1`](../../openai_wrapper/prompts.py) is
  dead and belongs to another project.
- `self.wa._send_message` ([`message_processor.py:174`](../../message_processor.py), `:193`) reaches
  into the wrapper's private method; prefer a public method of `whatsapp-wrapper`, or add one there.
- The `debug` flag is threaded through every `process_*` method to switch behaviour (rule 9 of the
  standard). Do not add more flag parameters; `mark_message_as_read` is never passed `False`.
- The "context not found" reply is written twice in `process_action`
  ([`message_processor.py:325`](../../message_processor.py), `:344`), and the "transcribe, log the
  failed stage" block twice (`process_audio`, `transcribe_again`). Extract instead of adding a third.
- Two OpenAI client styles: a module-level client in `chat.py`, one per call in `audio.py`.
- `app.py` reads `OPENAI_API_KEY` and never uses it, and calls `load_dotenv()` like `configs.py`:
  environment reading belongs in `configs.py`.
- `forward_to_local_dev` ([`app.py:23`](../../app.py)) returns a tuple on one path and `None` on the
  others, and the caller ignores both.
- `raise Exception(...)` and bare `except Exception` instead of specific types.
