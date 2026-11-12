# Bump a dependency, Python or the Heroku stack

Every rebuild can pick up drift: the first rebuild after two years moved to Python 3.14 and crashed
the bot (PR #4). Treat these as deploys.

## A dependency

1. Direct dependencies are pinned in [`requirements.in`](../../../requirements.in). Change the pin
   there (a new dependency needs Antonio's approval).
2. Regenerate the lock with the command at the top of
   [`requirements.txt`](../../../requirements.txt):
   `uv pip compile requirements.in -o requirements.txt --python-version 3.14 --python-platform x86_64-unknown-linux-gnu`.
   Never edit `requirements.txt` by hand.
3. Install the lock in a clean venv and run the smoke test ([`testing.md`](../testing.md)).
4. For `whatsapp-wrapper`, read its release notes: the code uses `MessageObject.base_data` and the
   private `_send_message`, which can change without notice.

Dependabot opens `chore(deps)` pull requests for transitive security bumps; they need only a green
smoke test.

## Python or the stack

1. Python: [`.python-version`](../../../.python-version) and the `--python-version` in the lock
   command, then regenerate the lock.
2. Heroku stack and buildpacks: [`app.json`](../../../app.json) (it applies to new apps only; the
   live app is moved with `heroku stack:set`, which Antonio runs or approves).
3. ffmpeg comes from the `heroku-buildpack-activestorage-preview` buildpack; keep it before
   `heroku/python`.
4. After the merge, check the deploy as [`testing.md`](../testing.md) says.
