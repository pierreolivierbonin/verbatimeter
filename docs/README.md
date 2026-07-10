# Documentation

## Guides

- [Using verbatimeter in a RAG agent](rag-agent-integration.md) — how to wire the
  verbatim check into a retrieval-augmented-generation loop.

## Architecture Decision Records

The rest of this folder records the architectural decisions behind `verbatimeter`
as ADRs (Architecture Decision Records). Each file is one decision, tagged
`ADR-NNNN`.

| ADR | Title | Status |
| --- | --- | --- |
| [ADR-0001](0001-standalone-package.md) | Standalone package, ported algorithm | Accepted |
| [ADR-0002](0002-candidate-side-lcs-alignment.md) | Candidate-side LCS alignment for word highlighting | Accepted |
| [ADR-0003](0003-best-segment-and-chunking.md) | Align against best contiguous segment; paragraph chunking | Accepted — segment clustering superseded by ADR-0012 |
| [ADR-0004](0004-tiktoken-token-counting.md) | tiktoken for differing-token counting | Accepted — API names superseded by ADR-0010 |
| [ADR-0005](0005-three-surfaces-and-source-resolution.md) | Library, decorator, and CLI surfaces | Accepted — API names superseded by ADR-0010 |
| [ADR-0006](0006-source-loading-optional-extras.md) | Text extraction is out of scope | Accepted — CLI path sniffing superseded by ADR-0013 |
| [ADR-0007](0007-scopes-and-ansi-rendering.md) | Two scopes and ANSI rendering | Accepted — `min_words` superseded by ADR-0011 |
| [ADR-0008](0008-thin-init-core-layout.md) | Thin `__init__.py`, implementation in `core.py` | Accepted |
| [ADR-0009](0009-contiguous-default-and-unicode-normalization.md) | Contiguous matching by default; Unicode-aware normalization | Accepted — `--min-run` superseded by ADR-0010 |
| [ADR-0010](0010-verbatim-overlap-whole-text-default.md) | Verbatim n-gram overlap; whole-text default; `ngram` replaces `min_run` | Accepted |
| [ADR-0011](0011-scope-verbatim-and-paraphrase.md) | Scope: verbatim reuse + verbatim paraphrasing; `ngram` sole knob (min 3); `min_words` removed; one provider example | Accepted |
| [ADR-0012](0012-match-window-rouge-and-reporting-fixes.md) | ROUGE-L over the full match window; punctuation-neutral fragments; stream-aware colour | Accepted |
| [ADR-0013](0013-explicit-inputs-single-tokenizer.md) | Explicit CLI file flags (no path sniffing); `--encoding` removed, bundled tokenizer only | Accepted |
| [ADR-0014](0014-functools-cache-memoization.md) | Compute-once values memoized with `functools.cache` | Accepted |
| [ADR-0015](0015-decorator-always-returns-result.md) | `verify` always returns the annotated answer; `return_result` removed, `print_stats` is the quiet-mode switch | Accepted |
| [ADR-0016](0016-spaced-script-multilingual-tier.md) | Spaced-script multilingual tier (11 validated languages); `casefold` replaces `lower` | Accepted |
| [ADR-0017](0017-automatic-streaming-verification.md) | `verify` auto-detects streamed (iterator) answers: live-coloured pass-through, `.result` on completion | Accepted |
