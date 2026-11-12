# Governance

## Truth hierarchy

Highest wins:

1. The code on `main`.
2. CI: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).
3. `CODEOWNERS` (none yet: Antonio reviews everything).
4. These pages.
5. [`AGENTS.md`](../../AGENTS.md) and the universal standard.
6. Tool layers: [`CLAUDE.md`](../../CLAUDE.md) and any other.

A contradiction is a bug in the lower source: stop and ask, or fix the lower one in its own change.

## Protected paths

Read freely; change only when the task asks for it.

| Path                                   | Why                                                                                       |
| -------------------------------------- | ----------------------------------------------------------------------------------------- |
| `Procfile`                             | One worker on purpose: the in-memory state needs it (`AGENTS.md`). A change is a deploy change. |
| `app.json`, `.python-version`          | Heroku stack, buildpacks (ffmpeg) and the Python version: a change rebuilds production.  |
| `requirements.in`, `requirements.txt`  | New dependencies need Antonio's approval. `requirements.txt` is **generated** by `uv pip compile` (command at its top); never edit it by hand. |
| `.github/workflows/**`                 | The smoke test gates the production deploy.                                               |
| `scripts/**`                           | They change config on the production Heroku app.                                          |
| `.env.template`                        | Lists every variable the app reads; keep it in step with `configs.py` and `app.py`.        |
| `LICENSE`                              | Not open source; never change it.                                                          |

## What an agent may do without asking

- Change the Python modules within the scope of the task, with the docs that go with it.
- Add or reword strings in `translations.py`, in all six languages.
- Run the app locally, the smoke test, and read-only Heroku commands
  (`heroku ps`, `heroku logs`, `heroku config:get`) on `axtwo-chaditt`.

## What an agent must ask about first

- Merging anything: a merge deploys to production. Antonio merges by hand.
- Any write to Heroku or Meta: `heroku config:set`, the `scripts/turn_*_testing.sh` scripts,
  restarts, add-ons (state the price first), webhook subscriptions.
- A new dependency, a new top-level module or package, a change of model or of its cost.
- Storing data outside memory (a database, a file): it changes privacy and the single-worker design.
- Logging anything a user said, or a full phone number.

## Meta-update map

Update the page in the same pull request as the change that makes it stale.

| When the change                                                    | Update                                     |
| ------------------------------------------------------------------ | ------------------------------------------ |
| adds, moves or splits a module                                     | `structure.md`, the layout in `AGENTS.md`  |
| adds a helper, a constant, a message key or a shared value         | `reusability.md`                           |
| changes how a message is routed, answered, logged or remembered    | `patterns.md`                              |
| adds tests, a test command or a manual check                       | `testing.md`                               |
| changes CI, a local gate or the PR conventions                     | `pr-and-ci.md`                             |
| changes the steps of a recurring kind of change                    | the page under `workflows/`                |
| adds an environment variable                                       | `.env.template`, the root `README.md`      |
| adds a rule every agent must know before any change                | `AGENTS.md`                                |
