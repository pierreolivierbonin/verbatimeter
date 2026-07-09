from openai import OpenAI

from verbatimeter import verify

SOURCE = (
    "We propose a new simple network architecture, the Transformer, based solely on "
    "attention mechanisms, dispensing with recurrence and convolutions entirely. "
    "Experiments on two machine translation tasks show these models to be superior in "
    "quality while being more parallelizable and requiring significantly less time to train."
)

SYSTEM_PROMPT = (
    "Answer using direct quotations from the passage. Put every quotation in double "
    "quotes, copy it verbatim, and quote at least three consecutive words."
)

client = OpenAI()


@verify(source_arg="source", scope="quotes")
def generate(question, source):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Passage:\n{source}\n\nQuestion: {question}"},
        ],
        temperature=0,
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    generate(
        "What architecture do the authors propose, and what does it dispense with?",
        source=SOURCE,
    )
