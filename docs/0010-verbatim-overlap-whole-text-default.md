# ADR-0010: Generalize to verbatim n-gram overlap; whole-text by default

Status: Accepted (supersedes parts of ADR-0007 and ADR-0009)

## Context

The tool was framed around checking an LLM's `"…"` quotations against a source.
But the quotation marks were only a **candidate selector** — a way to pick which
spans of the answer to score. The underlying, deterministic capability is more
general: *measure the verbatim n-gram overlap between any candidate text and a
source.* Tying the whole tool to quotation marks under-sold it (it also serves
extractiveness/copy-detection, memorization checks, and grounding-coverage) and
made "quote extraction" feel load-bearing when it is one optional layer.

Two secondary issues surfaced with the previous design:

- The threshold was named `min_run`, but users think of it as the *n* in
  "verbatim n-gram" — the minimum run length that counts.
- `check_quote` located the best-matching **source paragraph** and scored against
  it. That is correct for a short quotation (it comes from one place) but wrong
  for scanning a whole answer against a long source: overlap drawn from more than
  one paragraph was undercounted.

## Decision

1. **Whole-text is the default scope.** `check_answer(..., scope="all")` scores
   the entire candidate; `scope="quotes"` restricts to `"…"` spans (the
   hallucination-check application). The single-text primitive is `check(text,
   source, ...)`.
2. **`ngram` replaces `min_run`** everywhere (library kwarg and CLI `--ngram`),
   default 3. `min_run` is removed — no alias.
3. **Match against the whole source.** Paragraph chunking and best-chunk
   selection are gone; `check` aligns the candidate against the entire source in
   one pass, so verbatim runs from anywhere in the source are credited. The
   displayed segment is still the dominant matched cluster (ADR-0009).
4. **Reporting for the overlap use case.** `Result` (renamed from `QuoteResult`,
   field `quote` → `text`) gains `fragments` (the verbatim runs) and
   `longest_fragment`. The `Result.text`/`matched_ratio`/`differing_tokens` fields
   carry over.
5. **Renames for coherence.** The decorator is `verify` (was `verify_quotes`),
   defaulting to `scope="all"`. CLI: `--quotes` opts into quote scope, `--ngram`
   replaces `--min-run`, `--whole-answer` is removed (whole text is the default).
6. **Exit-code gate scoped to quotes.** The CI gate (non-zero exit on differing
   tokens) fires only under `scope="quotes"`, where differing = a fabricated
   quotation. Whole-text scope is a measurement and always exits 0.
   *Amended 2026-07-09:* the gate is now opt-in via `--fail` (replacing the
   opt-out `--no-fail`). Every scope is a measurement by default; the quotes
   scope's job is to highlight and score the quoted spans, and exit-code
   gating is a CI feature the caller requests explicitly.

## Consequences

- The tool reads as a general verbatim-overlap analyzer; the quotation/hallucination
  check is one application (`--quotes` / `scope="quotes"`), kept prominent because
  it is the sharpest, most marketable use.
- The "deterministic lower bound on hallucination" framing applies specifically to
  the quotes scope. Whole-text overlap measures **extractiveness/copying**, a
  different (also useful) quantity — documented so the two are not conflated.
- ADR-0007's two named scopes (`quotes` / `whole_answer`) become `quotes` / `all`
  with `all` as the default; ADR-0009's `min_run` naming is replaced by `ngram`.
  Both are superseded here.
- Matching a long candidate against a long source is now a single `O(m·n)` pass
  (no chunking); acceptable for typical sizes, with hashing/suffix-automaton
  speedups left as a future option.
