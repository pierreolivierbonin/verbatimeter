# ADR-0002: Candidate-side LCS alignment for word-level highlighting

Status: Accepted

## Context

The goal is to highlight, within a quotation, which individual words are
deterministically verbatim (present in the source) and which are not, and to
count the differing tokens.

CLaRA's `find_lcs_length` builds the LCS dynamic-programming table and, during
backtracking, records only the *reference-side* word indices (`i - 1`). It never
records which *candidate* (quote) words participate in the LCS, because CLaRA
only needs to locate and extract the matching source segment — not to classify
each quote word.

## Decision

Add a new function `lcs_alignment(reference_words, candidate_words)` that runs
the identical DP recurrence and backtrack but records **both** sides on each
match (`ref_idx.append(i-1)` and `cand_idx.append(j-1)`). It returns
`(lcs_length, ref_idx, cand_idx)`.

A candidate word at cleaned index `k` is classified verbatim iff
`k in set(cand_idx)`, otherwise differing. Original quote tokens are colored by
rebuilding a `clean_index -> original_token_index` map; tokens that disappear
under `clean_text` (pure punctuation) render neutral.

## Consequences

- Word-level green/red classification and the differing-token count fall directly
  out of `cand_idx`.
- `find_lcs_length` is kept unchanged (still used for segment location), so the
  two responsibilities stay separate and the port stays faithful.
- Classification inherits `clean_text` normalization — see ADR-0003 and
  ADR-0007 for the consequences (subsequence matching, case/punctuation).
