# Third-party notices

## tiktoken (OpenAI)

This package bundles the `cl100k_base` byte-pair-encoding vocabulary
(`src/verbatimeter/data/cl100k_base.tiktoken.gz`, SHA-256 of the uncompressed
file: `223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7`),
originally published by OpenAI at
`https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken`,
so that the default token counter works fully offline. The tokenizer pattern
string and special-token table in `src/verbatimeter/core.py` are copied from
[`tiktoken_ext/openai_public.py`](https://github.com/openai/tiktoken/blob/main/tiktoken_ext/openai_public.py).

tiktoken is licensed under the MIT License:

```
MIT License

Copyright (c) 2022 OpenAI, Shantanu Jain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
