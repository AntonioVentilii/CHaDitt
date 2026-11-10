# Agent docs

The long form behind [`AGENTS.md`](../../AGENTS.md). Read `AGENTS.md` first, then only the page you
need. The rules common to every repository are in the universal standard,
https://github.com/AntonioVentilii/officina/blob/main/standards/code.md; these pages add what is
specific to this one.

```
docs/ai/
├── README.md            you are here
├── governance.md        protected paths, what needs asking, the meta-update map
├── structure.md         the modules, where new code goes, the direction of imports
├── patterns.md          how a webhook is handled, replies, state, errors, logs; anti-patterns
├── reusability.md       the catalog of helpers, constants and strings that already exist
├── testing.md           the smoke test and how to verify a change by hand
├── pr-and-ci.md         title, body, the CI job, what to run before opening a PR
└── workflows/
    ├── add-message-or-language.md
    ├── add-action.md
    ├── change-openai-model.md
    └── update-dependencies.md
```

The [`README.md`](../../README.md) at the root is for people setting the bot up; these pages do not
repeat it.
