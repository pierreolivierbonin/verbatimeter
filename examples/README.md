# verbatimeter examples

Nothing here ships in the pip-installable package — everything under `examples/`
is excluded from the built wheel.

## [`basics/`](basics/) — run instantly, zero external deps

Library API, the `@verify` decorator, a custom tokenizer, and the CLI,
driven by a bundled passage and synthetic answers. Only `pip install verbatimeter`
is required. Start here.

```
cd examples/basics
python 01_library.py
```

## [`openai_example.py`](openai_example.py) — a live LLM behind the decorator

One real-provider integration: `@verify` wraps a `generate()` function that calls
OpenAI, extracts the answer's quotations, and prints the highlighted check as a
side effect. Requires `pip install openai` and `OPENAI_API_KEY` in the
environment.

```
pip install verbatimeter openai
python examples/openai_example.py
```

Every other provider (Anthropic, Gemini, Ollama, vLLM, Transformers, …) follows
the same pattern: decorate the function that returns the model's text and pass
the source text through the argument named by `source_arg`.

## [`rag_streaming_example.py`](rag_streaming_example.py) — a RAG agent with live-colored streaming

Simulates a retrieval-augmented agent: retrieves the best chunks for a query
and streams the model's answer through a `@verify`-decorated generator —
that's the whole integration. The decorator detects the streamed return value
and colors each word **as it streams** (green = verbatim from the retrieved
context, red = the model's own wording), passes the chunks through unchanged,
prints the stats line when the stream ends, and attaches the `CheckResult` as
`.result`. Requires `pip install openai` and `OPENAI_API_KEY`.

```
python examples/rag_streaming_example.py
```
