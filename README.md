# verbatimeter

Deterministically measure how much of a text **reuses** a source. Two readings
of one word-level alignment:

- **Verbatim reuse** (default) — word-for-word copying, in contiguous runs.
  Copied words are highlighted in one color, the rest in another, and the tokens
  that differ are counted.
- **Verbatim paraphrasing** (`--subsequence`) — the source's own words reused in
  order but not contiguously: split up, rearranged around, interleaved with new
  words. Paraphrase that stays verbatim at the word level.

No judge model, no embeddings, no sampling: run it twice, get the same numbers.

- **Source-use evaluation** — how much of a summary, answer, or document is
  taken directly from a reference, and how much verbatim-paraphrases it.
- **Hallucination gating (`--quotes`)** — instruct an LLM to support its answer
  with verbatim quotations, then verify them. A quotation whose words aren't in
  the source is a caught fabrication — a deterministic *lower bound* on grounding
  failures — and the exit code gates your pipeline.
- **English and French** — Unicode-normalized matching (NFC), and quotation
  extraction that understands straight `"…"`, curly `“…”`, guillemet `« … »`,
  and low-9 `„…“` conventions.
- **Lightweight and offline** — one runtime dependency (`tiktoken`), with the
  vocabulary bundled: no network access, ever.
- **Portable** — three surfaces for the same check: the `@verify` decorator over
  your LLM's `generate()` function, importable library functions, or a CLI.

It is built on a longest-common-subsequence (LCS) alignment ported from the
[Canada-Labour-Research-Assistant](https://github.com/pierreolivierbonin/Canada-Labour-Research-Assistant) project.

Scope is deliberately narrow: it verifies, highlights, and collects statistics on
text you provide. Extracting text from PDFs, Word documents, HTML, etc. is out of
scope — do that yourself with whatever library you prefer, then pass the text in.

## Install

```
pip install verbatimeter
```

`tiktoken` is the only runtime dependency, and it is only needed for the default
token counter (see [Tokenizer](#tokenizer)).

## Quickstart

No files, no quotation marks — paste this from any directory (`--source` /
`--answer` take literal text; add `--source-file` / `--answer-file` for paths):

```bash
verbatimeter \
  --source "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train." \
  --answer "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely"
```

Every word is verbatim, so it reports `matched=100% differing_tokens=0`. Change a
word in `--answer` — say `solely` to `partly` — and rerun: only that word turns
up in the differing color. (PowerShell: use backtick line-continuation and the
same quoting.)

To try the quotation/hallucination check instead, add `--quotes` and put a
`"…"` span in the answer. Runnable samples live in
[`examples/basics/`](examples/basics/).

## CLI

```
verbatimeter --source source.txt --source-file --answer answer.txt --answer-file
verbatimeter --source "raw source text" --answer - < answer.txt
verbatimeter --source source.txt --source-file --answer answer.txt --answer-file --quotes
verbatimeter --source source.txt --source-file --answer answer.txt --answer-file --ngram 5
```

- `--source` / `--answer` values are **literal text**; `--source-file` /
  `--answer-file` read them as UTF-8 file paths instead, and `--answer -` reads
  from stdin. Interpretation never depends on what happens to exist in the
  working directory.
- **Default scope is the whole text** (green = verbatim, red = not in the source).
  `--quotes` restricts the check to quoted spans (the hallucination-check use) —
  straight `"…"`, curly `“…”`, French guillemets `« … »` (inner padding spaces
  stripped), and low-9 `„…“`.
- Matching is **contiguous** by default: a word counts as verbatim only inside a
  run of `--ngram` (default 3, minimum 3 — shorter runs are coincidence-prone,
  especially with French and English function-word pairs) consecutive words copied
  verbatim from the source. A quotation shorter than `--ngram` words cannot contain
  such a run and therefore **fails the gate** — instruct your model to quote at
  least three consecutive words. `--subsequence` switches to order-only (LCS)
  matching, which measures **verbatim paraphrasing** — the source's words reused
  in order, not necessarily contiguously — and deliberately has no run floor
  (`--ngram` is ignored in this mode): single shared words in order are the
  signal.
- With `--quotes`, the exit code is non-zero when any quotation contains differing
  tokens — or when **no quotations are found at all** (an answer that stops quoting
  must not pass the gate silently). Disable with `--no-fail`. Whole-text scope is a
  measurement and always exits 0.
- `--no-color` for plain output (auto-disables on non-TTY / when `NO_COLOR` is
  set); `--json` emits machine-readable results.

## Library

```python
from verbatimeter import check, check_answer, render_result

# check one text against a source (verbatim n-gram overlap):
r = check(candidate_text, source_text, ngram=3)
print(r.matched_ratio, r.longest_fragment, r.fragments)

# or scope over an answer — the whole thing, or just its "…" quotations:
result = check_answer(answer, source, scope="all")      # or scope="quotes"
print(render_result(result))
print(result.total_differing_tokens)
```

`check(...)` returns a `Result` with `words` (per-word verbatim flags for
highlighting), `fragments` (the verbatim runs), `longest_fragment`,
`matched_ratio` (fraction of the text's words matched in the source),
`differing_tokens` / `total_tokens`, and `rouge_l` (ROUGE-L F1 between the text
and the smallest source window containing every matched word — how faithful the
text is to the region it drew from; `source_segment` is that window).

## Decorator

```python
from verbatimeter import verify

@verify(source_arg="context", scope="quotes")
def generate(prompt, context=None):
    return call_your_llm(prompt, context)

generate("...", context=retrieved_passages)
```

The wrapped function's return value is the answer; the source is resolved from a
static `source=` and/or a runtime argument (runtime wins). Highlighting and stats
print as a side effect — pass `print_stats=False` for a quiet mode — and the
answer comes back as a `str` subclass carrying the full measurement on
`.result` (a `CheckResult`), so existing string-handling code is unaffected and
the numbers are always one attribute away. Omit `scope="quotes"` to check the
whole answer.

Integrating with a retrieval-augmented-generation agent? See
[docs/rag-agent-integration.md](docs/rag-agent-integration.md).

## Tokenizer

The differing-token count uses `tiktoken` (encoding `cl100k_base`) by default.
The vocabulary is bundled with the package (see
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)), so token counting works fully
offline — the package never touches the network. To count with a different
tokenizer — or avoid `tiktoken` entirely — pass a `count_tokens` callable
(`str -> int`) to `check`, `check_answer`, or `verify`:

```python
check_answer(answer, source, count_tokens=lambda text: len(text.split()))
```

When `count_tokens` is supplied, `tiktoken` is never imported.

## Performance

verbatimeter is a word-level dynamic-programming alignment. Let **S** be the
number of words in the source and **C** the number of words in the text being
checked (the whole answer with `scope="all"`, or the total quoted words with
`scope="quotes"`).

| Step | Time | Memory |
| --- | --- | --- |
| Clean / tokenize | O(S + C) | O(S + C) |
| Contiguous match (default) | O(S · C) | O(C) — two rolling DP rows |
| Subsequence match (`--subsequence`) | O(S · C) | O(S · C) — full DP table |
| ROUGE-L score | O(S · C) | O(C) — two rolling DP rows |
| Token counting (tiktoken) | O(C) | — |

End-to-end time is **O(S · C)**, dominated by the alignment. Contiguous keeps only
the current and previous DP rows (`O(C)` memory) and runs a few times faster than
subsequence, which materializes the whole `S × C` table.

Measured with [`profiling/benchmark.py`](profiling/benchmark.py) (random text,
best of 5; absolute times are hardware-dependent):

```
S (source)  C (cand)        S*C   contiguous   subsequence   ns/(S*C)
       500       100      50000        2.2ms         8.1ms       43.7
      1000       100     100000        3.8ms        19.0ms       37.7
      2000       100     200000        8.0ms        33.4ms       40.1
      4000       100     400000       15.3ms        65.8ms       38.3
      1000       400     400000       14.9ms        65.9ms       37.4
      1000       800     800000       29.9ms       135.5ms       37.4
      4000       400    1600000       53.4ms       263.6ms       33.4
```

The `ns/(S·C)` column stays flat as both S and C grow — the O(S·C) time confirmed
in practice. For typical inputs (a few-thousand-word context, a few-hundred-word
answer) that is single-digit to tens of milliseconds. Very large sources grow
quadratically; contiguous n-gram matching could be reduced to O(S + C) with
rolling hashes or a suffix automaton (noted as a future option in
[ADR-0010](docs/0010-verbatim-overlap-whole-text-default.md)).

## Sample text

All example text in this README and throughout [`examples/`](examples/) is quoted
verbatim from:

> Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N.,
> Kaiser, Ł., & Polosukhin, I. (2017). *Attention Is All You Need.* Advances in
> Neural Information Processing Systems 30. arXiv:[1706.03762](https://arxiv.org/abs/1706.03762).

## Design

Architecture decisions are recorded as ADRs under [`docs/`](docs/), alongside the
[RAG integration guide](docs/rag-agent-integration.md).
