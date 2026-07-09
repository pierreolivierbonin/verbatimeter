# ADR-0004: Use tiktoken for the differing-token count

Status: Accepted

## Context

A headline requirement is counting the number of *tokens* within a quotation that
differ from the source. "Tokens" implies a subword tokenizer, not a word count.
CLaRA counts tokens with a HuggingFace `PreTrainedTokenizerFast` loaded from a
9.5 MB Llama tokenizer file, which drags in `transformers` (and effectively
torch). That is far too heavy for a minimal, portable tool.

## Decision

Use `tiktoken` (OpenAI's BPE tokenizer), default encoding `cl100k_base`, as the
single runtime dependency. The differing-token count is
`counter(" ".join(differing_words))`, where `differing_words` are the cleaned
candidate words not in the LCS; `total_tokens` is `counter(quote)`.

The tokenizer is pluggable: `check_quote` / `check_answer` / `verify_quotes`
accept a `count_tokens` callable (`str -> int`). When it is omitted, the default
counter uses `tiktoken` with the selected `encoding`; when supplied, the caller's
tokenizer (a HuggingFace tokenizer, a word splitter, anything) is used and
`tiktoken` is never imported. `tiktoken` is imported lazily at first default use
and encoders are cached, so the pure `align` layer stays dependency-free.

## Consequences

- Base install is light (`tiktoken` only) and fast.
- The token count is a provider-neutral proxy; it will not exactly equal any
  specific model's tokenizer, which is acceptable for a hallucination-extent
  signal.
- First use of an encoding downloads its BPE file (one-time network access) and
  pulls in `regex` transitively. Documented as a caveat.
