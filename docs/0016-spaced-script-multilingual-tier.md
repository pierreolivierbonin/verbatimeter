# ADR-0016: Spaced-script multilingual tier; case folding

**Status:** Accepted
**Date:** 2026-07-09
**Extends:** the English/French goal in ADR-0011.

## Context

The matching pipeline assumes exactly one thing about a language: words are
separated by whitespace. Everything else is already script-neutral — NFC
normalization (ADR-0012 era), Unicode category-P punctuation stripping (which
covers the Devanagari danda `।`, the Arabic comma `،`, the Urdu full stop `۔`,
and fullwidth CJK marks), the four quotation conventions, and byte-level BPE
token counting. That makes every spaced-script language a validation problem,
not an engineering problem.

Two gaps existed:

1. `clean_text` used `str.lower()`, which is not full Unicode case folding:
   uppercase `SCHLIESST` failed to match `schließt` because `ß` only folds to
   `ss` under `str.casefold()`.
2. Nothing beyond English and French was actually tested, so no claim could
   honestly be made.

## Decision

1. **`clean_text` case-folds** (`str.casefold()` instead of `str.lower()`).
   Folding is strictly more permissive and deterministic; English and French
   behavior is unchanged.
2. **A parametrized validation suite** (`tests/test_multilingual.py`) covers
   Spanish, Portuguese, German, Russian, Hindi, Bengali, Indonesian, Urdu, and
   Arabic — for each: a verbatim excerpt matches 100%, an altered word is
   flagged, and the language's native quotation convention round-trips through
   the quotes scope. CLI gate tests cover one right-to-left script (Arabic)
   and one Indic script (Hindi) end to end. Test sentences are deliberately
   neutral in content (library opening hours) and identical in theme across
   languages.
3. **PyPI Natural Language classifiers** are declared for the eleven validated
   languages (all verified against the official trove list).

## Limitations, stated deliberately

- **Arabic is validated unvocalized.** Text with harakat (combining marks,
  category Mn) will not match its unvocalized form; targeted diacritic
  normalization is future work, distinct from blanket mark-stripping (which
  would corrupt Indic scripts).
- **Unsegmented scripts (Chinese, Japanese, Thai) are out of scope** until a
  character-level matching mode or a pluggable segmenter exists; the README
  says so explicitly rather than failing quietly.
- Test sentences were authored, not sourced from native corpora; a native
  review pass before marketing per-language claims is prudent.

## Consequences

- The honest claim expands from two languages to eleven, at the cost of one
  changed line in `clean_text` and one test module.
- Case-insensitive matching now handles `ß`/`SS` and full Cyrillic folding.
- The whitespace assumption is now written down as the package's one
  language-support boundary, giving the CJK decision (future ADR) a precise
  starting point.
