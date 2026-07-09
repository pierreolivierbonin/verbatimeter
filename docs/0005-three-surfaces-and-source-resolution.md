# ADR-0005: Library, decorator, and CLI surfaces; decorator source resolution

Status: Accepted

## Context

The tool must be maximally portable: usable as an importable library, hookable
into an existing app or webapp with minimal effort, and runnable from the command
line for quick experiments.

For the decorator, the source text to check against can be known statically at
decoration time, or arrive per-call (e.g. a RAG function that receives its
retrieved context as an argument). Both must be supported.

## Decision

Expose three surfaces over a single core (`check_answer` / `check_quote`):

1. **Library** — `check_answer`, `check_quote` returning `CheckResult` /
   `QuoteResult` dataclasses; `render_result` for presentation.
2. **Decorator** — `@verify_quotes(...)`. It calls the wrapped function to obtain
   the answer string, resolves the source with the **runtime keyword argument
   winning** over the static `source=` (`kwargs[source_arg]` if present, else the
   static value), runs the check, and prints highlighting + stats as a side
   effect. It returns the original answer unchanged; with `return_result=True` it
   returns an `AnnotatedAnswer(str)` subclass carrying `.result`, so `str(x)` is
   still the raw answer. If no source resolves, it is a no-op passthrough.
3. **CLI** — `verbatimeter`, an argparse entry point over the same core.

## Consequences

- One code path (`check_answer`) is shared by all three surfaces; behavior is
  consistent.
- The decorator never breaks a host application: unresolved source or a
  non-string return value passes through untouched.
- `AnnotatedAnswer` subclassing `str` keeps existing call sites working while
  making structured results available when asked for.
