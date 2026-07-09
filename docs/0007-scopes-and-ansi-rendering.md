# ADR-0007: Two scopes and ANSI terminal rendering

Status: Accepted

## Context

Two ways of checking an answer are useful: verifying only the explicitly
`"..."`-quoted spans (the model's claimed quotations), and verifying the entire
answer as one candidate (how faithful is the whole response). Each should be
visually distinguishable and carry its own statistics.

CLaRA's highlighting is HTML/CSS for Streamlit. This tool targets the terminal,
which has no existing color infrastructure in the source project.

## Decision

Support two scopes in `check_answer`:

- `quotes` (default) — extract each `"..."` span (deduped, `min_words` filter) and
  check it; render verbatim green, differing red.
- `whole_answer` (opt-in) — check the full answer as a single candidate; render
  verbatim cyan, differing magenta.

Render with raw ANSI escape codes. Color auto-resolves to on only when
`sys.stdout.isatty()` and `NO_COLOR` is unset; it can be forced off
(`--no-color` / `use_color=False`). Punctuation-only tokens render without color.
The CLI also offers `--json` for machine-readable output and exits non-zero when
any quotation has differing tokens (overridable with `--no-fail`) so it can gate
CI.

## Consequences

- The two scopes are immediately distinguishable by color and each prints its own
  stats block plus an aggregate summary.
- Piping to a file or another process yields clean, un-colored text automatically;
  the `NO_COLOR` convention is honored.
- Quote extraction uses `r'"([^"]*)"'` and does not handle nested or curly quotes;
  documented as a known limitation.
