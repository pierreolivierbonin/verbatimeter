# ADR-0003: Align against the best contiguous segment; chunk by paragraph

Status: Accepted

## Context

An LCS is a *subsequence*, not a substring. If a quote is aligned directly
against a large source, common words ("the", "shall", "of") can match at
scattered, unrelated positions, inflating the apparent verbatim ratio and
understating hallucination.

Separately, the DP table is `O(m*n)` in time and memory. Running it against an
entire large document (e.g. a PDF) for a long candidate is slow and memory-heavy.

## Decision

For each candidate, first call
`find_segment_with_longest_common_subsequence(quote, chunk)` to locate the
best-matching **contiguous** source segment (it already prefers the earliest,
ROUGE-L-optimal span). Then run `lcs_alignment` against only that segment's
words. This localizes the match to the region the quote actually came from.

Split the source into paragraphs (on blank lines) and evaluate each chunk
separately, keeping the highest-scoring segment. This bounds each DP table to a
single paragraph.

## Consequences

- Spurious subsequence matches are sharply reduced; the alignment reflects a real
  contiguous region of the source.
- Large documents stay tractable because no single DP table spans the whole text.
- Residual risk remains for repeated common tokens *within* one segment; this is
  accepted and documented rather than solved.
- A quote that legitimately spans two paragraphs is scored against whichever
  single paragraph matches best. Acceptable for the intended use.
