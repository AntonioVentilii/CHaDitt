# Testing

There is no unit test suite yet. Adding one (pytest, a `tests/` folder, a dev requirements file) is
a new dependency and a new folder: ask Antonio first. The pure helpers are the natural first
targets: `split_text`, `parse_reply_id`, `action_from_typed_choice`, `language_for_wa_id`,
`get_localized_message`.

## The CI smoke test

[`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), job `smoke-test`, runs on every pull
request and on `main`, and Heroku waits for it before deploying:

1. Install the locked requirements on the Python of `.python-version`, with ffmpeg.
2. `import app` with dummy credentials, the way gunicorn loads it.
3. Generate an ogg/opus voice note and convert it to mp3 with `convert_audio_to_mp3`.

Run the same locally before a pull request:

```bash
GRAPH_API_TOKEN=x MOBILE_ID=x OPENAI_API_KEY=x python -c "import app"
```

## Checking a change by hand

A change to how messages are handled is checked with a real message before it merges, and the pull
request says what was checked.

- **Pure logic or prompts:** call the function from a Python shell with the real OpenAI key in `.env`
  (as PR #12 did for language detection and a correction).
- **The webhook flow:** run `flask run`, expose it with `scripts/start_ngrok.sh`, then turn on testing
  mode with `scripts/turn_on_testing.sh` (asks for the ngrok URL; production then forwards every
  webhook to `/test/webhook` here). Only senders in `DEBUG_CHAT_IDS` are answered, with replies
  prefixed `*DEBUG*`. Always run `scripts/turn_off_testing.sh` afterwards: testing mode left on in
  production forwards to a dead URL. Both scripts write to the production app, so ask first.
- **After a merge:** `heroku ps -a axtwo-chaditt` shows `web.1: up`, `GET /` answers 200
  `Audio Transcription Running`, and a voice note gets 👂, the transcription, then ✅.
