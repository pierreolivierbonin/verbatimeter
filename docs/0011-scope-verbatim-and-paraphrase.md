# ADR-0011: Scope — verbatim reuse and verbatim paraphrasing, one strictness knob

**Status:** Accepted
**Date:** 2026-07-09
**Supersedes:** the `min_words` quote filter (part of ADR-0007) and the
multi-provider examples tier described in earlier docs.

## Context

The package's surface had accumulated features beyond its core competence, and a
multi-agent code review traced its weakest findings to exactly those features.
The goal is a repository that can claim one specific job done very well:

- measuring and highlighting **verbatim reuse** of source text in a generation;
- measuring and highlighting **verbatim paraphrasing** of source text in a
  generation — the source's own words reused in order but not contiguously
  (order-only subsequence matching); not semantic paraphrase detection, which
  is an NLI problem and out of scope;
- in both **English and French**;
- **lightweight** — a single runtime dependency (`tiktoken`), fully offline by
  default;
- **portable** — three surfaces: the `@verify` decorator over any `generate()`
  function, importable library functions, and a CLI.

Two strictness parameters coexisted: `ngram` (the minimum contiguous run that
counts as verbatim) and `min_words` (a pre-filter dropping short quotations).
Their interaction was a trap: with the defaults (`ngram=3`, `min_words=1`), a
two-word quotation could never pass the gate — too short to contain a three-word
run — and nothing explained why. The two names also suggested two matching
concepts where the algorithm has only one.

## Decision

1. **`min_words` is removed** from `extract_quotes`, `check_answer`, `verify`,
   and the CLI. Whitespace-only quotes are still dropped during extraction.
   *Amended 2026-07-09:* extraction now also strips surrounding whitespace
   uniformly across conventions and drops quotes containing no clean word
   (punctuation-only spans), which previously slipped through the gate with
   zero countable tokens.
2. **`ngram` is the single strictness knob**, with an enforced minimum of 3
   (`check` raises `ValueError` below it). Shorter runs are coincidence-prone,
   especially with English and French function-word pairs (*of the*, *in a*,
   *de la*, *que le*, *il y*).
   *Amended 2026-07-12:* the floor is enforced only in contiguous mode, where
   `ngram` is used. Subsequence mode documents `ngram` as ignored, and
   validating a parameter that has no effect contradicted that contract —
   `check(..., mode="subsequence", ngram=1)` now succeeds instead of raising.
3. **Quotations shorter than `ngram` words fail closed** in the quotes gate:
   they cannot contain the evidentiary unit, so they are unverified, not
   skipped. The documented contract is to instruct the model to quote at least
   three consecutive words. Silently skipping short quotes would recreate, in
   miniature, the zero-quotes silent pass the gate was hardened against.
4. **Subsequence mode has no run floor by design.** Single shared words in
   order are the signal; the mode's numbers are documented as verbatim
   paraphrasing, not verbatim evidence.
5. **Provider examples are reduced to one** (`examples/openai_example.py`,
   OpenAI, decorator-based). Every other provider follows the same pattern; the
   previous seven-integration tier was maintenance surface tied to fast-moving
   SDKs.

## Consequences

- One name, one concept: no parameter interaction to misconfigure or document.
- `--min-words` disappears from the CLI; `extract_quotes(answer)` loses its
  second parameter. No compatibility impact — the package is unreleased.
- Short-quote failures are intentional and prompt-fixable, and the README says
  so where the gate is described.
- The examples tree carries one external-SDK dependency surface instead of six.
