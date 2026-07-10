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

## [`openai_rag_streaming_example.py`](openai_rag_streaming_example.py) — a RAG agent with live-colored streaming

One real-provider integration: a retrieval-augmented agent that retrieves the
best chunks for a query and streams the model's answer through a
`@verify`-decorated generator — that's the whole integration. The decorator
detects the streamed return value and colors each word **as it streams**
(green = verbatim from the retrieved context, red = the model's own wording),
passes the chunks through unchanged, prints the stats line when the stream
ends, and attaches the `CheckResult` as `.result`. Requires
`pip install openai python-dotenv` and `OPENAI_API_KEY` in the environment or
a `.env` file.

```
python examples/openai_rag_streaming_example.py
```

Every other provider (Anthropic, Gemini, Ollama, vLLM, Transformers, …) follows
the same pattern: decorate the function that returns the model's text and pass
the source text through the argument named by `source_arg`.
