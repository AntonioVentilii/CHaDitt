# Pull requests and CI

## Title

One plain imperative sentence that says what changes for the bot or its users, no prefix, no
trailing period. From the history:

- `Run one gunicorn worker so button taps find their transcription`
- `Move off retired OpenAI models`
- `Ignore webhooks for other phone numbers and make side calls best effort`

Dependabot's `chore(deps): ...` titles stay as they are. One pull request has one scope, whatever
its size: a title that needs "and" between two things is two pull requests (rule 2 of the standard,
scoped). Pull requests start in parallel from `main`; stack one on another only when it needs the
other's code (rule 3, parallel, not stacked).

## Body

Three sections, as every recent pull request has them:

```
## Why
What was broken or missing, with the evidence (a log line, an error, a date).

## What changes
The change, a table when comparing before and after (models, prices, limits).

## Testing
What was run and what was checked by hand (see testing.md); unchecked boxes for what can only be
checked after the deploy.
```

No AI attribution lines. No line starts with `Test:` or `Fix:`.

## CI

One workflow, [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), job `smoke-test`, on
every pull request and on pushes to `main`. Heroku deploys `main` only after it is green, so a red
smoke test on `main` blocks production. What it runs: [`testing.md`](./testing.md).

## Before opening a pull request

1. `pip install -r requirements.txt` in a clean venv when the lock changed.
2. The smoke test: `GRAPH_API_TOKEN=x MOBILE_ID=x OPENAI_API_KEY=x python -c "import app"`.
3. The manual check that fits the change ([`testing.md`](./testing.md)).
4. The docs pages the change makes stale ([`governance.md`](./governance.md#meta-update-map)).

## Merging

Antonio merges every pull request by hand: never merge, never turn on auto-merge. A merge is a
production deploy, so a pull request that changes runtime behaviour says in its Testing section how
to check it after the deploy.
