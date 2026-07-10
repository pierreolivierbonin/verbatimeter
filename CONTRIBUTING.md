# Contributing

## Scope

verbatimeter does one job: deterministic verification of how grounded an
AI-generated text is in its source. The scope is recorded in
[ADR-0011](docs/0011-scope-verbatim-and-paraphrase.md) and defended
deliberately — features and improvement requests that expand it will usually
be declined, however well built. Open an issue before writing a feature PR;
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

along with the expected result, the actual result, and the output of
`verbatimeter --version`. The bug-report form requires these fields. Reports
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

- **No comments, no docstrings.** All prose lives in the README and the ADRs
  under [`docs/`](docs/). Explain a decision in an ADR, not next to the code.
- **Behavioral or design changes require an ADR** (`docs/NNNN-title.md`,
  numbered sequentially) recording context, decision, and consequences.
  Superseded decisions get a dated amendment, never a silent rewrite.
- **Every bug fix ships a regression test.** Every feature ships tests for its
  behavior and its failure modes.
- **Test fixtures use neutral content** (the existing suites use library
  opening hours) and, for multilingual work, the language's native quotation
  conventions.
