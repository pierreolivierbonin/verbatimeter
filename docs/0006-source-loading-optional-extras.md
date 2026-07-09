# ADR-0006: Text extraction is out of scope

Status: Accepted (supersedes an earlier plan for built-in PDF/DOCX/HTML loaders)

## Context

An early design shipped source loaders for PDF, DOCX, and HTML behind optional
pip extras (`pymupdf4llm`, `python-docx`, `beautifulsoup4`). Each format needs a
third-party parser. The overriding project values are: as few dependencies as
possible (ideally zero) and no try-except control flow. Bundled extractors
conflict with both — they add dependencies and their "install the extra, else
raise" pattern is exactly the kind of exception-driven control flow we reject.

## Decision

Remove all text-extraction code and dependencies. The package operates purely on
text that the caller provides. Extracting text from PDFs, Word documents, HTML,
or anything else is the caller's responsibility, using whatever library they
prefer.

The CLI still accepts a file path for `--source` / `--answer` and reads it as
UTF-8 text with the standard library (no third-party parser, no format
detection); a value that is not a file is treated as literal text, and `-` reads
the answer from stdin.

## Consequences

- The package has no extraction dependencies; `tiktoken` (ADR-0004) is the only
  runtime dependency.
- Scope is sharply defined: verify, highlight, and collect statistics — nothing
  else.
- Passing a non-text file (e.g. a raw `.pdf`) to the CLI yields garbage, because
  no extraction is attempted. This is intended: the caller must extract first.
