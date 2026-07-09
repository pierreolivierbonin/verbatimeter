from verbatimeter import check_answer, render_result
from qa_pairs import SOURCE, pairs, failure, print_source

print_source()


def compare(label, answer):
    print(f"##### {label}")
    print(answer)
    print("\n--- mode='contiguous'  (default: only >=3-word verbatim runs count) ---")
    print(render_result(check_answer(answer, SOURCE, scope="quotes", mode="contiguous")))
    print("\n--- mode='subsequence'  (order-only LCS: verbatim paraphrasing) ---")
    print(render_result(check_answer(answer, SOURCE, scope="quotes", mode="subsequence")))
    print()


scattered = (
    'A loose summary claims the passage says "the model computes value vectors from the inputs".'
)
compare("Words lifted from the source but reordered - not a real excerpt", scattered)

compare(
    "A genuine near-verbatim quote - on real excerpts the two modes mostly agree", failure(pairs[1])
)

print("Contiguous (default) only credits >=3-word verbatim runs, so scattered words score 0%.")
print("Subsequence credits any in-order overlap - the looser reading is verbatim paraphrasing.")
