# Basics — zero-dependency demos

Runnable examples exercising each application `verbatimeter` was built for. They
need **no external services or API keys** — just `pip install verbatimeter` — and
import the installed package exactly as an external consumer would.

`source.txt` holds excerpts quoted verbatim from *Attention Is All You Need*
(Vaswani et al., 2017; arXiv:[1706.03762](https://arxiv.org/abs/1706.03762)) — a
passage most developers will recognize. `qa_pairs.py` holds 6 items, each
mimicking a user asking a language model about that passage and telling it to
quote directly. Each item is a **controlled A/B on the same excerpt**: a `success`
answer that reproduces the quotation verbatim, and a `failure` answer with the
*identical* surrounding prose and the *identical* quotation except for a few
swapped words. Run side by side, the only visible difference is the handful of
words the model failed to reproduce, shown in red. (`success()` / `failure()`
build the two answers from shared prose so they can differ only inside the
quotation.)

Run from this directory (`cd examples/basics`):

- **Library API** — `python 01_library.py`
  Shows one item in full — the success answer (quotation all green, 0 differing
  tokens) directly above the failure answer (same quotation, altered words red) —
  then a one-line A/B summary for the remaining items. What an eval script would
  use: `check_answer` + `render_result`, then `differing_tokens` / `rouge_l`.

- **Decorator / app integration ("hook")** — `python 02_decorator.py`
  A mock `generate()` wrapped with `@verify(scope="quotes")`, called once for the
  correct quotation and once for the slipped one. Highlighting + stats print
  automatically and the app still gets its answer back (with `.result` attached).

- **Custom tokenizer / zero-dependency** — `python 03_custom_tokenizer.py`
  Passes a `count_tokens` callable so tiktoken is never imported, and compares
  total differing tokens under tiktoken vs. a stdlib word count across the failure
  answers.

- **Matching modes (contiguous vs. subsequence)** — `python 04_matching_modes.py`
  Renders the same quotation under the default `mode="contiguous"` and the
  opt-in `mode="subsequence"` (the CLI's `--subsequence`). Shows why contiguous
  is the default: subsequence matches words in order regardless of adjacency, so
  it over-credits scattered or reordered words as "verbatim."

- **Whole-text verbatim overlap** — `python 05_overlap.py`
  No quotation marks at all: the default scope scans the entire text for runs of
  ≥ `ngram` words copied from the source. Contrasts an extractive summary (high
  overlap) with an abstractive one (near-zero), and shows the `ngram` threshold in
  action. This is the general-purpose engine; demos 01–04 are the quote-check
  application built on top of it.

- **CLI** — quick experiments (the demos 01–04 check quotations, so pass
  `--quotes`; without it the CLI scans the whole answer, like demo 05):
  ```
  verbatimeter --source-file source.txt --answer-file answer.txt --quotes
  verbatimeter --source-file source.txt --answer-file answer.txt --quotes --subsequence
  verbatimeter --source-file source.txt --answer-file answer.txt
  verbatimeter --source-file source.txt --answer-file answer.txt --quotes --json
  cat answer.txt | verbatimeter --source-file source.txt --answer-file - --quotes
  ```
  The third form (no `--quotes`) scans the whole answer, like demo 05. Every
  scope exits 0 by default; add `--fail` to use `--quotes` as a CI gate whose
  exit code becomes non-zero when any quotation contains differing tokens or
  when no quotations are found.

Colors are shown in a real terminal; when output is piped or redirected they
auto-disable (honoring `NO_COLOR`).
