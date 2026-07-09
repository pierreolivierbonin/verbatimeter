# ADR-0013: Explicit CLI inputs; single bundled tokenizer

**Status:** Accepted
**Date:** 2026-07-09
**Supersedes:** the file-path sniffing described in ADR-0006 and the
`--encoding` option from ADR-0004's surface.

## Context

Two mechanisms undermined claims the package wants to make.

First, the CLI guessed whether `--source` / `--answer` values were file paths:
any value naming an existing file was read from disk. A literal answer that
happened to collide with a filename in the current working directory was
silently replaced by that file's contents, so the same command produced
different measurements in different directories — a quiet wrong-measurement in
exactly the CI-gate setting the tool targets. Explicit `--source-file` /
`--answer-file` flags already existed alongside the heuristic.

Second, `--encoding` accepted any tiktoken encoding name. Only `cl100k_base` is
bundled; every other name re-opened the network download path that bundling was
introduced to eliminate, making "works offline" true only for the default.

## Decision

1. **CLI inputs are literal text unless explicitly flagged.** `--source-file` /
   `--answer-file` read the value as a UTF-8 file path; `--answer -` reads
   stdin. The `os.path.isfile` sniffing is removed. Input interpretation never
   depends on the working directory's contents.
2. **`--encoding` is removed, along with the `encoding` parameter** on `check`,
   `check_answer`, and `verify`. The bundled `cl100k_base` encoder is the only
   built-in token counter, and the `count_tokens` callable (`str -> int`)
   covers every other tokenizer without importing `tiktoken` at all. The
   package makes no network access under any configuration.

## Consequences

- Deterministic input handling: a command line means the same thing everywhere.
- File-based invocations are slightly longer (`--source src.txt --source-file`);
  the README and examples show the flagged forms.
- The offline guarantee is unconditional and testable, and the internal encoder
  cache collapses from a dict keyed by encoding name to a single lazy instance.
- Counting in another model's token units is done via `count_tokens`, which is
  also the escape hatch for avoiding `tiktoken` entirely.
