# ADR-0015: The decorator always returns the annotated answer

**Status:** Accepted
**Date:** 2026-07-09
**Supersedes:** the `return_result` opt-in from ADR-0005.

## Context

`verify` had two output channels behind two switches: `print_stats` (default
on) controlled the printed report, and `return_result` (default off)
controlled whether the caller received a plain `str` or an `AnnotatedAnswer`
carrying the `CheckResult`. With the defaults, the measurement was computed,
printed, and discarded; with `print_stats=False` and the default
`return_result=False`, the decorator computed a full check and reported it to
no one — a silent no-op flagged by code review, with no test covering the
quiet branch.

The opt-in existed to keep the return value maximally unsurprising, but
`AnnotatedAnswer` is a `str` subclass: every consumer that treats the answer
as a string (printing, concatenation, serialization, API payloads) behaves
identically whether or not the result rides along.

## Decision

`verify` always returns `AnnotatedAnswer(answer, result)` when a check ran;
`return_result` is removed. `print_stats` stays and now controls exactly one
thing — console output — so `print_stats=False` is a legitimate quiet mode:
compute, attach `.result`, print nothing. Both modes are tested.

The pass-through cases are unchanged: when no source resolves or the wrapped
function returns a non-string, the original value comes back untouched, with
no `.result` attribute.

## Consequences

- The measured values are always one attribute away (`answer.result`);
  gating no longer requires foresight at decoration time.
- One less parameter, and no configuration combination that discards the
  measurement silently.
- Callers that transform the answer (slicing, concatenation) get plain `str`
  back — the annotation does not survive string operations, which is inherent
  to subclassing `str` and acceptable: gate first, transform after.
- Code relying on `type(answer) is str` (rare; `isinstance` is unaffected)
  would newly see `AnnotatedAnswer` — no such usage exists in the repository,
  and the package is unreleased.
