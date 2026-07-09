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
