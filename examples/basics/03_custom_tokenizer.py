from verbatimeter import check_answer, render_result
from qa_pairs import SOURCE, pairs, failure

word_count = lambda text: len(text.split())

print("=== one FAILURE answer, rendered with a stdlib word counter (no tiktoken) ===")
print(
    render_result(check_answer(failure(pairs[0]), SOURCE, scope="quotes", count_tokens=word_count))
)

tk_total = sum(
    check_answer(failure(p), SOURCE, scope="quotes").total_differing_tokens for p in pairs
)
wc_total = sum(
    check_answer(failure(p), SOURCE, scope="quotes", count_tokens=word_count).total_differing_tokens
    for p in pairs
)

print(f"\n=== differing tokens across all {len(pairs)} FAILURE answers ===")
print(f"  tiktoken (cl100k_base): {tk_total}")
print(f"  stdlib word count     : {wc_total}")
print("\nSame alignment, different counting unit. Any str->int callable works:")
print("a HuggingFace tokenizer, a model-specific BPE, or this word counter.")
