# Contributing

## Scope

verbatimeter does one job: deterministic verification of how grounded an
AI-generated text is in its source. That scope is defended deliberately —
features and improvement requests that expand it will usually be declined,
however well built. Open an issue before writing a feature PR;
an undiscussed feature PR risks being closed on scope grounds alone.

Bug reports and bug-fix PRs are encouraged and prioritized.

## Reporting a bug

Every bug report must include a reproducible example that works out of the
box — exact inputs inline, no local files, runnable as pasted:

```python
from verbatimeter import check

r = check("the answer text that misbehaves", "the source text")
print(r.matched_ratio, r.fragments)
```

along with the expected result and the actual result. The bug-report form
requires these fields. Reports
without a runnable reproduction will be sent back for one before triage.

## Development setup

```
git clone https://github.com/pierreolivierbonin/verbatimeter
cd verbatimeter
uv sync
uv run pre-commit install
uv run pytest
```

Every commit must pass the pre-commit gauntlet — gitleaks, ruff check,
ruff format, ty — and the full test suite. CI runs the suite on Python
3.10–3.13 across Ubuntu and Windows.

## Conventions

- **Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):**
  `type: description` — e.g. `feat:`, `fix:`, `docs:`, `test:`, `build:`, `chore:`.
  PR titles use the same format, since a squash merge takes the PR title
  as the commit subject.
- **No comments, no docstrings.** All prose lives in the README and the docs
  under [`docs/`](docs/). Explain a decision in its PR, not next to the code.
- **The PR is the decision record** for behavioral and design changes: state
  the context, the decision, and its consequences in the PR description.
- **Every bug fix ships a regression test.** Every feature ships tests for its
  behavior and its failure modes.
- **Test fixtures use neutral content** (the existing suites use library
  opening hours) and, for multilingual work, the language's native quotation
  conventions.
