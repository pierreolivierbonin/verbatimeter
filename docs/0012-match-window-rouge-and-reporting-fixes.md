# ADR-0012: ROUGE-L over the full match window; reporting fixes

**Status:** Accepted
**Date:** 2026-07-09
**Supersedes:** the best-cluster segment selection in ADR-0003.

## Context

A multi-agent code review confirmed three defects in how results were computed
and reported:

1. `segment_span` clustered matched source indices with a gap tolerance of
   `max_gap = len(idx)` and kept only the largest cluster. The tolerance was an
   emergent property of the match count rather than a tunable or meaningful
   quantity, and `rouge_l` was then scored against that single cluster while
   `matched_ratio`, `differing_tokens`, and the word highlighting counted
   matches from *all* clusters. An answer stitching two verbatim runs from
   opposite ends of a source reported `matched=100%` beside `rouge_l=0.667` —
   two headline numbers computed over different match sets, with the divergence
   arbitrary rather than interpretable.
2. `_fragments` treated punctuation-only tokens (a standalone em-dash, an
   ellipsis) as run breakers, even though `clean_text` drops them before
   alignment. A four-word run interrupted by an em-dash reported
   `longest_run=2` — below the `ngram=3` threshold that was required for the
   match to exist at all.
3. Colour auto-detection always interrogated `sys.stdout`, so
   `verify(file=log)` wrote ANSI escape sequences into the log file whenever
   the process's stdout happened to be a terminal.

## Decision

1. **`source_segment` is the full match window**: the smallest span of the
   source containing every matched word, from the first matched index to the
   last. No clustering, no `max_gap` heuristic. `rouge_l` is the ROUGE-L F1
   between the candidate and that window. The two headline statistics now have
   distinct, stated meanings over the *same* match set: `matched_ratio` is
   candidate-side verbatim coverage ("how much of this text appears in the
   source"), `rouge_l` is window fidelity ("how faithful is this text to the
   region it drew from"). They can legitimately diverge — a text that stitches
   fragments from a wide region scores high coverage and low fidelity — and
   that divergence is now a signal, not an artifact.
2. **Punctuation-only tokens are neutral in fragment runs**: they neither break
   a run nor count toward its length. A punctuation token inside a run is kept
   in the fragment's display text; trailing punctuation after a run is not.
   `longest_fragment` counts clean words (via `clean_text`), consistent with
   every other word count in the package.
3. **Colour resolution is stream-aware**: `render_result` accepts the output
   stream and auto-detection asks *that* stream whether it is a terminal.
   `verify(file=...)` passes its target stream, so files never receive ANSI
   codes unless colour is forced with `use_color=True`.

## Consequences

- `matched_ratio` and `rouge_l` are computed over the same match set; reports
  are internally consistent and each number has a one-line definition (stated
  in the README and the RAG guide).
- The `rouge_l` of a scattered match drops toward its true fidelity instead of
  being inflated or deflated by cluster selection; the worked example in the
  RAG guide is unchanged (its matches were contiguous).
- `segment_span` is simpler and faster (no clustering pass).
- Fragment statistics can no longer contradict the `ngram` threshold.
- Programmatic consumers of `verify(file=...)` output get clean text.
