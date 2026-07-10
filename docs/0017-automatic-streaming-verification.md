# ADR-0017: Automatic streaming verification in the decorator

**Status:** Accepted
**Date:** 2026-07-09
**Extends:** ADR-0015.

## Context

LLM applications stream. Before this decision, a `@verify`-decorated function
that returned a generator fell through the decorator's `isinstance(answer,
str)` guard: the stream passed to the caller unverified, silently — the same
failure mode class as the positional-source and zero-quotes bugs fixed
earlier. The streaming RAG example worked only by hand-rolling ~40 lines of
incremental checking outside the package.

A design constraint from the incremental-colouring problem: a word's verdict
can change while the stream is still running, but only in one direction and
only in one place. Matched words are final (a contiguous run never shrinks as
text is appended); the only words whose verdict can flip red-to-green are the
trailing words that still align with a contiguous source sequence shorter
than `ngram` — the growing edge of a potential run. Everything before that
edge is stable.

## Decision

No streaming parameter. `verify` detects an `Iterator` return value and wraps
it in an `AnnotatedStream`:

1. **Pass-through preserved** — iterating the `AnnotatedStream` yields the
   original chunks unchanged, so the caller's own streaming UI is unaffected.
2. **Live colouring** (whole-text scope, contiguous mode, `print_stats=True`)
   — as chunks arrive, words are printed to the output stream in their final
   colour with a lookahead lag of at most `ngram - 1` words (the stable-edge
   rule above), append-only: no cursor movement, no repainting. A trailing
   partial word is held until whitespace completes it.
3. **Post-hoc reporting** for quotes scope or subsequence mode — live
   colouring is not attempted there (quote spans are not identifiable until
   closed; subsequence match sets are not append-monotonic). The stream
   passes through and the ordinary rendered report prints on completion.
4. **`.result` after exhaustion** — the full `CheckResult` is attached to the
   `AnnotatedStream` once the stream completes, mirroring `AnnotatedAnswer`.
   `print_stats=False` remains the quiet mode: pass-through and `.result`
   only.

## Consequences

- A streaming `generate()` needs exactly the same one-line decoration as a
  non-streaming one; the RAG example shrank from a page of machinery to a
  generator with `@verify` on it.
- Each word boundary re-runs the contiguous check on the accumulated text —
  O(S·C) per update. Fine at chat-stream rates and demo sizes; a future
  incremental DP could reduce it if livestreaming very long generations ever
  matters.
- Strings are not `Iterator`s, so the existing string path is untouched;
  non-string, non-iterator returns still pass through unverified as before.
- The live stats tail duplicates `render_result`'s per-result stats line
  format; the words themselves were already printed incrementally, so the
  full renderer cannot be reused without reprinting them.
