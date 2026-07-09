# ADR-0009: Contiguous matching by default; Unicode-aware normalization

Status: Accepted (supersedes parts of ADR-0002 and ADR-0003)

## Context

A review of the matching core surfaced four issues:

1. **Normalization gap.** `clean_text` stripped only ASCII `string.punctuation`
   plus curly double quotes. Curly apostrophes (`’`), en/em dashes (`– —`), and
   ellipsis (`…`) were left in, so a quotation identical to the source except for
   typography (which LLMs emit constantly) was scored as hallucinated.
2. **Subsequence ≠ verbatim.** LCS matches words in order but not contiguously,
   so scattered or reordered words counted as "verbatim" even when they were not
   a real contiguous excerpt.
3. **Heuristic segment refinement.** `find_lcs_length`'s optimal-segment logic
   scored sub-ranges with `lcs_length - i`, a lower bound on the true LCS — the
   chosen boundaries were best-effort, not principled.
4. **Redundant work.** `check_quote` built a DP table twice (segment location,
   then candidate alignment) and recomputed ROUGE-L several times; the full
   `O(m·n)` matrix was materialized even for length-only needs.

## Decision

1. **Normalize all Unicode punctuation.** `clean_text` now strips any character
   in `string.punctuation`, an explicit set of common Unicode quotes/dashes, and
   anything in Unicode category `P*`. ASCII behavior (removal, not spacing) is
   preserved; typography-only differences no longer register as differing.
2. **Contiguous matching is the default.** `contiguous_alignment` marks a
   candidate word verbatim only if it lies in a run of at least `min_run`
   (default 3) consecutive words that appears verbatim as consecutive words in
   the source. Subsequence matching (`lcs_alignment`) remains available via
   `mode="subsequence"` (`--subsequence` on the CLI). ROUGE-L is still reported
   as the classic subsequence metric, computed over the located segment.
3. **One mode-aware pass, no heuristic.** `find_lcs_length` and
   `find_segment_with_longest_common_subsequence` are removed. `check_quote`
   makes a single alignment pass per source paragraph (contiguous or LCS),
   derives the displayed segment directly from the matched source-word indices
   via `segment_span`, and keeps the best-scoring paragraph.
4. **Cheaper DP.** `contiguous_alignment` uses rolling rows (`O(n)` memory), and
   the segment/char-offset mapping lives in one helper (`word_char_spans` /
   `segment_span`) instead of being duplicated.

`mode` and `min_run` are threaded through `check_quote`, `check_answer`, and
`verify_quotes`; the CLI exposes `--subsequence` and `--min-run`.

## Consequences

- Smart quotes, apostrophes, and dashes no longer produce false hallucination
  flags.
- Highlighting reflects actual contiguous verbatim excerpts; scattered/reordered
  word matches are no longer counted as verbatim. A genuinely isolated one-word
  match between two edits is not marked (a single word is not a verbatim quote) —
  an accepted, deliberate consequence of `min_run` defaulting to 3 (a two-word coincidence no longer counts as a verbatim quote).
- `find_lcs_length` / `find_segment_with_longest_common_subsequence` (referenced
  in ADR-0002 and ADR-0003) no longer exist; that behavior is superseded here.
  `lcs_alignment` is retained for `mode="subsequence"` and for the ROUGE-L stat.
