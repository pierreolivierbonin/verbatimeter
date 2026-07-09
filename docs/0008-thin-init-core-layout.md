# ADR-0008: Thin `__init__.py`, implementation in `core.py`

Status: Accepted

## Context

An earlier consolidation put the entire library and CLI (~215 lines) directly in
`__init__.py`, leaving only `align.py` separate. The motivation was minimizing
file count. On review this conflicts with the prevailing Python convention: the
official Python Packaging User Guide keeps `__init__.py` empty or minimal and
puts logic in named modules, and widely used packages follow suit — Flask's
`__init__.py` is only re-exports, Requests' is setup plus re-exports, with the
implementation living in dedicated modules.

Reasons the convention holds: everything in `__init__.py` runs on any import of
the package (import cost and side effects); a heavy `__init__` that submodules
import back into invites circular imports; and readers/tools expect
`__init__.py` to be the package's table of contents, not its implementation.

## Decision

Split the package into three files:

- `align.py` — the pure LCS/ROUGE-L algorithm (ADR-0001).
- `core.py` — the tool: quote extraction, token counting, `check_*`, dataclasses,
  rendering, the decorator, and the CLI `main`.
- `__init__.py` — a thin façade that re-exports the public API from `core` and
  `align` and declares `__version__` / `__all__`.

The console entry point stays `verbatimeter:main`, resolved through the
`__init__` re-export.

## Consequences

- Layout matches the mainstream convention; `__init__.py` reads as the public API
  index.
- One more file than the previous two-file layout — an accepted, deliberate cost,
  chosen over both the against-convention heavy `__init__` and a single-module
  distribution that would mix the dense DP code with the CLI.
- Importing `verbatimeter` still exposes the same names; no change for callers.
