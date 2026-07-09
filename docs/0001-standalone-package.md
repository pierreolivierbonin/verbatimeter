# ADR-0001: Standalone package with a ported algorithm

Status: Accepted

## Context

The verbatim-quotation algorithm we want originates in the
Canada-Labour-Research-Assistant (CLaRA) project's `src/citation.py`. CLaRA is a
Streamlit + ChromaDB + vLLM/Ollama RAG application with a very heavy dependency
footprint (torch, transformers, vLLM). We want a small tool that LLM researchers
and AI engineers can `pip install` and drop into any workflow.

The relevant CLaRA functions (`clean_text`, `calculate_rouge_L_score`,
`find_lcs_length`, `find_segment_with_longest_common_subsequence`) are
stdlib-only, but the module begins with `from config import QuotationsConfig`,
coupling it to CLaRA's configuration.

## Decision

Create a new, standalone sibling package (`verbatimeter`) rather than extending
CLaRA. Port the four pure functions into `align.py` verbatim, removing the
`config` import; thresholds and minimums become plain function arguments. Do not
import CLaRA at runtime.

## Consequences

- Base install depends only on `tiktoken`; none of CLaRA's heavy stack is pulled
  in.
- The ported functions are duplicated, not shared. If CLaRA fixes a bug in the
  LCS core, it must be re-ported. This is an accepted cost for independence.
- The package is reusable outside the Canadian-labour-law domain.
