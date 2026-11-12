# AGENTS.md

The entry point for every coding agent working in this repository (Claude Code, Cursor, Codex,
Copilot and the rest). It is short on purpose: the detail lives under [`docs/ai/`](./docs/ai/).

## What this repository is

C'Ha Ditt?! is a WhatsApp bot. A Flask app ([`app.py`](./app.py)) receives Meta's WhatsApp Cloud
API webhook, transcribes voice notes with OpenAI and answers with the transcription and three reply
buttons: correct, summarize and translate (a menu of languages). It runs on Heroku as the app
`axtwo-chaditt` ([`scripts/config.sh`](./scripts/config.sh)), Python 3.14
([`.python-version`](./.python-version)), with ffmpeg from a buildpack ([`app.json`](./app.json)).

Things that are not obvious from the code:

- **A merge to `main` is a production deploy.** Heroku deploys `main` once CI is green. There is no
  staging app.
- **State lives in memory, in one process.** Languages and transcriptions are dicts on
  `MessageProcessor` ([`message_processor.py:121`](./message_processor.py)); the
  [`Procfile`](./Procfile) runs one gunicorn worker with threads so a button tap reaches the process
  that sent the transcription. Never raise the worker count; a restart forgets everything, and the
  buttons survive it by downloading the voice note again.
- **The webhook is shared.** Meta can deliver messages for other numbers too: anything whose
  `metadata.phone_number_id` is not `MOBILE_ID` is ignored
  ([`message_processor.py:215`](./message_processor.py)).

## Commands

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt          # the lock; ffmpeg must be on PATH for audio
flask run                                # dev server on :5000, reads .env (see .env.template)
gunicorn app:app --workers 1 --threads 8 # what Heroku runs
GRAPH_API_TOKEN=x MOBILE_ID=x OPENAI_API_KEY=x python -c "import app"  # the CI smoke test
pip install -r requirements-dev.txt && ruff check .  # the quality gate (and npx jscpd@5.4.2 .)
uv pip compile requirements.in -o requirements.txt --python-version 3.14 --python-platform x86_64-unknown-linux-gnu
```

The last line regenerates the lock after a change to [`requirements.in`](./requirements.in).

## Layout

| Path                                      | What it holds                                                       |
| ----------------------------------------- | ------------------------------------------------------------------- |
| [`app.py`](./app.py)                      | Flask routes: verification, webhook, test webhook, local forwarding |
| [`configs.py`](./configs.py)              | WhatsApp settings read from the environment                         |
| [`message_processor.py`](./message_processor.py) | Everything a webhook triggers: routing, replies, state, logs |
| [`translations.py`](./translations.py)    | Every user-facing string in six languages, language detection by number |
| [`openai_wrapper/`](./openai_wrapper/)    | OpenAI calls: transcription, chat, language detection; models and prompts |
| [`scripts/`](./scripts/)                  | Heroku testing-mode toggles and ngrok, run by hand from `scripts/`  |
| [`.github/workflows/ci.yml`](./.github/workflows/ci.yml) | The CI smoke test that gates the deploy              |

More in [`docs/ai/structure.md`](./docs/ai/structure.md).

## The standard

Every change follows the universal code standard:
https://github.com/AntonioVentilii/officina/blob/main/standards/code.md. It is not repeated here;
cite its rules by number and name ("rule 5, one value, one place"). This repository adds only:

- **Strings for people live in [`translations.py`](./translations.py)**, in all six languages at once
  (rule 5). Prompts for the model live in [`openai_wrapper/`](./openai_wrapper/), in English.
- **Model names live only in [`openai_wrapper/models.py`](./openai_wrapper/models.py)**, with their
  price and retirement date in the comment.
- **WhatsApp limits are named constants** at the top of
  [`message_processor.py`](./message_processor.py); never a bare 1024 or 20 elsewhere.
- **One log line per outcome**, through `log_outcome` ([`message_processor.py:52`](./message_processor.py)):
  senders masked to four digits, never the text of a message or a transcription.
- **Side calls are best effort** (reactions, read receipts, the failure message): they log and never
  raise. The main answer raises, so Meta retries.
- **A change to the webhook flow is checked against a real voice note** before merging, since there
  is no test suite yet ([`docs/ai/testing.md`](./docs/ai/testing.md)).

## Before you change something, read

| You are about to                                  | Read first                                                                 |
| ------------------------------------------------- | -------------------------------------------------------------------------- |
| change anything                                   | [`docs/ai/governance.md`](./docs/ai/governance.md)                         |
| add a module or move code                         | [`docs/ai/structure.md`](./docs/ai/structure.md)                           |
| write a helper, a constant or a string            | [`docs/ai/reusability.md`](./docs/ai/reusability.md)                       |
| handle a message, log, react or reply             | [`docs/ai/patterns.md`](./docs/ai/patterns.md)                             |
| add or reword a message, or a language            | [`docs/ai/workflows/add-message-or-language.md`](./docs/ai/workflows/add-message-or-language.md) |
| add a reply button or change what one does        | [`docs/ai/workflows/add-action.md`](./docs/ai/workflows/add-action.md)     |
| change an OpenAI model or prompt                  | [`docs/ai/workflows/change-openai-model.md`](./docs/ai/workflows/change-openai-model.md) |
| bump a dependency, Python or the Heroku stack     | [`docs/ai/workflows/update-dependencies.md`](./docs/ai/workflows/update-dependencies.md) |
| test or verify a change                           | [`docs/ai/testing.md`](./docs/ai/testing.md)                               |
| open a pull request                               | [`docs/ai/pr-and-ci.md`](./docs/ai/pr-and-ci.md)                           |

## Truth hierarchy

Highest wins: the code on `main`, then CI, then `CODEOWNERS` (none yet), then `docs/ai/**`, then this
file, then tool layers ([`CLAUDE.md`](./CLAUDE.md) and the like). On a contradiction, stop and ask.

## Keep these docs true

A change that adds a pattern, a shared helper, a constant, a convention or a workflow updates the
matching `docs/ai/` page in the same pull request. Which page covers what:
[`docs/ai/governance.md#meta-update-map`](./docs/ai/governance.md#meta-update-map).
