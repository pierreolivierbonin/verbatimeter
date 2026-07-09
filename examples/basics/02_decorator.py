from verbatimeter import verify
from qa_pairs import SOURCE, pairs, print_source, success, failure

print_source()


@verify(source=SOURCE, scope="quotes")
def generate(question, altered=False):
    pair = next(p for p in pairs if p["question"] == question)
    return failure(pair) if altered else success(pair)


q = pairs[0]["question"]
print("=== decorated generate(): the @verify hook prints on every call ===")
print(f"user asks: {q}\n")

print("--- model quotes correctly ---")
generate(q)

print("\n--- model slips (same quotation, a few words changed) ---")
generate(q, altered=True)
