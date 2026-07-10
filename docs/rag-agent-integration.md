# Using verbatimeter in a RAG agent

This is a how-to guide (not an ADR). It shows where `verbatimeter` fits in a
retrieval-augmented-generation loop and the exact steps to wire it in. The
package already supports everything below — no extra code is required.

## Where it fits

A RAG agent normally does: **retrieve → prompt → generate → answer**.
`verbatimeter` adds one deterministic step at the end:

```
user query
   │
   ▼
retrieve relevant chunks ─────────────►  context (the source of truth)
   │                                          │
   ▼                                          │
prompt the model to quote verbatim            │
   │                                          │
   ▼                                          │
model answer with "…" quotations              │
   │                                          │
   ▼                                          ▼
verbatimeter.check_answer(answer, context) ◄──┘
   │
   ▼
per-quote verdict: which words are verbatim, how many tokens differ
   │
   ▼
display highlighting  ·  gate the answer  ·  re-prompt if fabricated
```

`verbatimeter` checks the model's **quotations** against the retrieved context.
It does not judge paraphrased claims — its job is: *of the text the model put in
quotation marks, how much was actually copied verbatim from the sources.*

## Prerequisites

```
pip install verbatimeter
```

`verbatimeter`'s only runtime dependency is `tiktoken` (a tokenizer used for the
differing-token count), which `pip` installs automatically. It has **no**
dependency on any LLM client, vector store, or agent framework — it operates
purely on the two strings you already have (the retrieved context and the model's
answer). If you'd rather not pull in `tiktoken`, pass your own `count_tokens`
callable (see [Tuning](#tuning)); it is then never imported.

## Step 1 — Retrieve, and join the chunks into one `source`

Use your existing retriever and concatenate the retrieved chunks into one string
(blank lines between them read naturally). `check_answer` matches quotations
against the **entire** source, so a quote copied from any chunk is credited.

```python
def retrieve(query: str) -> str:
    chunks = vector_store.search(query, k=5)      # your retriever
    return "\n\n".join(c.text for c in chunks)     # the source of truth
```

## Step 2 — Tell the model to quote verbatim

The check only works on spans the model wraps in quotation marks, so instruct it
to do exactly that (this is the same system prompt used in
[`examples/openai_example.py`](../examples/openai_example.py)):

```python
SYSTEM_PROMPT = (
    "Answer using direct quotations from the passage. Put every quotation in double "
    "quotes, copy it verbatim, and quote at least three consecutive words."
)
```

## Step 3 & 4 — Generate, then verify

Two ways to wire in the check. Pick by whether you want a drop-in side effect or
programmatic control.

### Option A — the decorator (drop-in)

Wrap your generation function. The source is resolved from the runtime `context`
argument (set `source_arg` to the parameter name your function uses). Highlighting +
stats print automatically (pass `print_stats=False` for a quiet mode), and the
answer comes back still usable as a plain string, with the `CheckResult`
attached as `.result`.

Pass `scope="quotes"` — verbatimeter defaults to scanning the whole answer, but
here you only want to check the model's `"…"` quotations.

```python
from verbatimeter import verify

@verify(source_arg="context", scope="quotes")
def generate(query: str, context: str) -> str:
    return call_your_llm(system=SYSTEM_PROMPT, context=context, query=query)

context = retrieve(query)
answer = generate(query, context=context)         # prints the verbatim report
# answer.result is a CheckResult you can inspect or gate on
```

### Option B — explicit check (for gating)

Call `check_answer` yourself when you want to act on the verdict.

```python
from verbatimeter import check_answer, render_result

context = retrieve(query)
answer = call_your_llm(system=SYSTEM_PROMPT, context=context, query=query)

result = check_answer(answer, context, scope="quotes")
print(render_result(result))                       # highlighted, for logs/CLI
```

## Step 5 — Act on the verdict

`CheckResult` gives you the signal to gate on. `total_differing_tokens == 0` means
every quotation was copied verbatim; anything above zero means the model altered
or invented words inside quotation marks.

```python
if result.total_differing_tokens > 0:
    fabricated = [q for q in result.results if q.differing_tokens > 0]
    # choose a policy:
    #   • surface the highlighted answer to the user with a warning, or
    #   • reject and re-prompt ("quote the sources exactly; do not alter wording"), or
    #   • fail closed in a pipeline / CI gate
```

Per-quote fields on each `result.results[i]` (a `Result`):

| Field | Meaning |
| --- | --- |
| `text` | the model's quoted span |
| `source_segment` | the smallest passage window containing every matched word |
| `words` | per-word `WordSpan(text, verbatim)` — drives the highlighting |
| `fragments` / `longest_fragment` | the verbatim runs, and the longest run length |
| `differing_tokens` / `total_tokens` | altered/invented tokens vs. the quote's size |
| `matched_ratio` | fraction of quote words that are verbatim |
| `rouge_l` | ROUGE-L F1 of the quote vs. `source_segment` — fidelity to the region it drew from |

## Worked example

The whole check on a concrete source — sentences quoted verbatim from *Attention
Is All You Need* (Vaswani et al., 2017; arXiv:1706.03762):

```python
from verbatimeter import check_answer, render_result

source = (
    "The dominant sequence transduction models are based on complex recurrent or "
    "convolutional neural networks in an encoder-decoder configuration. The best "
    "performing models also connect the encoder and decoder through an attention "
    "mechanism. We propose a new simple network architecture, the Transformer, based "
    "solely on attention mechanisms, dispensing with recurrence and convolutions "
    "entirely. Experiments on two machine translation tasks show these models to be "
    "superior in quality while being more parallelizable and requiring significantly "
    "less time to train."
)

answer = (
    'According to the abstract, "We propose a new simple network architecture, the '
    'Transformer, based solely on attention mechanisms, dispensing with recurrence and '
    'convolutions entirely". A careless summary instead reports the "Experiments on two '
    'machine translation tasks show these models to be inferior in quality while being '
    'more portable".'
)

print(render_result(check_answer(answer, source, scope="quotes")))
```

Output — the faithful quotation checks out, the careless one is caught:

```
[1] We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely
    matched=100%  differing_tokens=0/25  longest_run=20  rouge_l=1.000

[2] Experiments on two machine translation tasks show these models to be inferior in quality while being more portable
    matched=89%  differing_tokens=3/19  longest_run=11  rouge_l=0.914

2 result(s)  total_differing_tokens=3  mean_rouge_l=0.957
```

The first quotation is reproduced word-for-word (`differing_tokens=0`); the second
swapped `superior`→`inferior` and `parallelizable`→`portable`, and verbatimeter
flags exactly those — a fabricated quotation caught deterministically.

> Fittingly, the source excerpts above were themselves verified verbatim with
> verbatimeter (`check(excerpt, source).differing_tokens == 0`) before being
> pasted here.

## Tuning

- **Strictness** — matching is contiguous by default (`ngram=3`: a word counts as
  verbatim only inside a run of ≥3 consecutive copied words; 3 is also the
  minimum). Raise `ngram` to tighten, or use `mode="subsequence"` for order-only
  matching, which measures verbatim paraphrasing — the source's words reused in
  order, not necessarily contiguously (`ngram` is ignored in this mode). All
  accepted by `check` / `check_answer` / `verify`.
- **Tokenizer** — the differing-token count uses tiktoken (`cl100k_base`) by
  default. To count with your model's own tokenizer (or avoid tiktoken), pass a
  `count_tokens` callable: `check_answer(answer, context, count_tokens=my_tok)`.
- **Scope** — `scope="quotes"` (used here) checks each `"…"` span. The default
  `scope="all"` checks the entire answer as one candidate — useful for a "how
  much of the whole response is lifted verbatim from the context" view.

## What it does and does not do

- ✅ Deterministically verifies **quoted** text against the retrieved context and
  quantifies fabrication token-for-token. No model, no API call, no flakiness.
- ⚠️ It checks quotations, not **paraphrase faithfulness** — a claim stated
  without quotation marks is not evaluated (that is an NLI / grounding problem,
  out of scope here).
- ⚠️ It is **post-hoc**: run it on the completed answer (for streaming, check when
  the stream finishes, or per paragraph).
- ⚠️ It reports *which passage region* matched (`source_segment`) but not *which
  retrieved document id* — the `source` is one text blob. For per-document
  attribution, run `check_answer` against each chunk separately and keep the
  best-scoring one, or map `source_segment` back to your chunk metadata.

## See also

- A runnable live-provider integration:
  [`examples/openai_example.py`](../examples/openai_example.py).
- Zero-setup demos of the library, decorator, and CLI:
  [`examples/basics/`](../examples/basics/).
