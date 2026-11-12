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

One workflow, [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml), on every pull request
and on pushes to `main`. Heroku deploys `main` only after it is green, so a red job on `main` blocks
production.

- `smoke-test`: install the lock, `import app`, convert a voice note ([`testing.md`](./testing.md)).
- `quality-gate`: the mechanical limits below.

## The quality gate

- **ruff** ([`ruff.toml`](../../ruff.toml), version pinned in
  [`requirements-dev.txt`](../../requirements-dev.txt)): pyflakes and pycodestyle errors, lines of
  120, and for every function: complexity, branches, returns, statements, arguments, nesting depth,
  no boolean flag parameters, no commented-out code. The limits are in `ruff.toml`.
- **jscpd** ([`.jscpd.json`](../../.jscpd.json)): no duplicated block in the Python code
  (threshold 0%, today's value).
- **File length**: 300 lines per Python file; the step in `ci.yml` holds the limit and the caps.

The functions already over a limit carry `# noqa: <rule>` on their `def` line, and the files over
300 lines have a cap at today's size. Ruff's RUF100 fails on a `noqa` that is no longer needed, so
the baseline only shrinks: when a change brings a function under a limit, remove its `noqa`; when it
shrinks a capped file, lower or remove its cap. Never add a `noqa`, raise a limit or a cap, or
loosen the threshold to get to green (rule 11 of the standard): split the function instead.

## Before opening a pull request

1. `pip install -r requirements.txt` in a clean venv when the lock changed.
2. The smoke test: `GRAPH_API_TOKEN=x MOBILE_ID=x OPENAI_API_KEY=x python -c "import app"`.
3. The gate: `pip install -r requirements-dev.txt && ruff check .`, then `npx jscpd@5.4.2 .`.
4. The manual check that fits the change ([`testing.md`](./testing.md)).
5. The docs pages the change makes stale ([`governance.md`](./governance.md#meta-update-map)).

## Merging

Antonio merges every pull request by hand: never merge, never turn on auto-merge. A merge is a
production deploy, so a pull request that changes runtime behaviour says in its Testing section how
to check it after the deploy.
