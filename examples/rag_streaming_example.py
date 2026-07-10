import os

from dotenv import load_dotenv
from openai import OpenAI

from verbatimeter import verify
from verbatimeter.align import clean_text

load_dotenv()

KNOWLEDGE = [
    (
        "transformer-architecture",
        "We propose a new simple network architecture, the Transformer, based solely on "
        "attention mechanisms, dispensing with recurrence and convolutions entirely.",
    ),
    (
        "translation-results",
        "Experiments on two machine translation tasks show these models to be superior in "
        "quality while being more parallelizable and requiring significantly less time to train.",
    ),
    (
        "scaled-dot-product",
        "We suspect that for large values of d_k, the dot products grow large in magnitude, "
        "pushing the softmax function into regions where it has extremely small gradients.",
    ),
    (
        "multi-head-attention",
        "Multi-head attention allows the model to jointly attend to information from different "
        "representation subspaces at different positions.",
    ),
]

SYSTEM_PROMPT = (
    "Answer the question in one short paragraph of plain text, reusing the exact wording "
    "of the context wherever you can. No quotation marks, no markdown."
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def retrieve(query, k=2):
    query_words = set(clean_text(query))
    ranked = sorted(
        KNOWLEDGE,
        key=lambda chunk: len(query_words & set(clean_text(chunk[1]))),
        reverse=True,
    )
    return ranked[:k]


@verify(source_arg="source")
def generate(question, source):
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{source}\n\nQuestion: {question}"},
        ],
        temperature=0,
        stream=True,
    )
    for event in stream:
        delta = event.choices[0].delta.content or ""
        if delta:
            yield delta


if __name__ == "__main__":
    question = "What architecture does the paper propose, and why is it faster to train?"
    chunks = retrieve(question)
    print(f"query      : {question}")
    print(f"retrieved  : {', '.join(title for title, _ in chunks)}")
    print()
    print("streaming answer (green = verbatim from retrieved context, red = model's own words):")
    print()
    source = "\n\n".join(text for _, text in chunks)
    answer = generate(question, source=source)
    text = "".join(answer)
