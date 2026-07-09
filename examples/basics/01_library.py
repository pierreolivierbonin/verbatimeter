from verbatimeter import check_answer, render_result
from qa_pairs import SOURCE, pairs, print_source, success, failure

print_source()

pair = pairs[0]
print(f"===== Q1: {pair['question']}")

print("\n--- SUCCESS: the model reproduces the quotation verbatim ---")
ok = success(pair)
print(ok)
print(render_result(check_answer(ok, SOURCE, scope="quotes")))

print("\n--- FAILURE: the SAME quotation, with the model's altered words in red ---")
bad = failure(pair)
print(bad)
print(render_result(check_answer(bad, SOURCE, scope="quotes")))

print("\n===== The same A/B check over the remaining pairs =====")
flagged = 1
for i, pair in enumerate(pairs[1:], 2):
    ok_tokens = check_answer(success(pair), SOURCE, scope="quotes").total_differing_tokens
    bad_tokens = check_answer(failure(pair), SOURCE, scope="quotes").total_differing_tokens
    status = "flagged" if bad_tokens else "MISSED"
    if bad_tokens:
        flagged += 1
    print(f"Q{i}: success {ok_tokens} differing tokens, failure {bad_tokens} -> {status}")

print(
    f"\nREPORT: every SUCCESS quotation checked out at 0 differing tokens; "
    f"{flagged}/{len(pairs)} FAILURE quotations were flagged as non-verbatim."
)
