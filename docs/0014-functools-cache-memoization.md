# ADR-0014: Memoize compute-once values with functools.cache

**Status:** Accepted
**Date:** 2026-07-09

## Context

The bundled tokenizer encoder is expensive to build (decompressing the
vocabulary and constructing a ~100k-entry rank table, on the order of a few
hundred milliseconds) and is needed at most once per process. It must also stay
lazy: `import verbatimeter`, `--help`, and callers supplying their own
`count_tokens` must never pay for it (ADR-0013).

The original implementation hand-rolled the memo with a module-level sentinel:

```python
_ENCODER = None

def _tiktoken_count(text):
    global _ENCODER
    if _ENCODER is None:
        _ENCODER = _bundled_cl100k_base()
    return len(_ENCODER.encode(text))
```

This works, but it spreads one idea across three constructs (a sentinel global,
a `global` declaration, and a `None` check), and the `global` rebinding is a
recurring source of reader confusion.

## Decision

Compute-once values are memoized by decorating their builder with
`functools.cache`:

```python
@cache
def _bundled_cl100k_base(): ...

def _tiktoken_count(text):
    return len(_bundled_cl100k_base().encode(text))
```

The semantics are identical to the sentinel version: nothing runs at import,
the first call builds the value, and the cache holds a strong reference for
the life of the process. Tests reset state with
`_bundled_cl100k_base.cache_clear()` instead of reassigning a global.

This is the house pattern for any future compute-once value. It does not apply
to values that are cheap module-level constants (compiled regexes, ANSI codes),
which stay as plain assignments, nor to per-object state captured in closures
(such as the decorator's `inspect.signature(fn)`), which is already computed
exactly once per decorated function.

## Consequences

- One construct instead of three; no module global and no `global` statement.
- Laziness and process-lifetime retention are inherited from the standard
  library rather than asserted by hand.
- A concurrent first call may build the encoder twice under free-threaded
  Python; both results are equivalent and one wins — harmless for a pure
  builder.
- The encoder was the only hand-rolled memo in the codebase at the time of
  this decision; a repository scan found no other instances.
