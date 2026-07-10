import verbatimeter
from verbatimeter import check_answer, extract_quotes

SOURCE = "alpha beta gamma delta epsilon zeta eta theta"


def test_unclosed_quote_is_ignored():
    assert extract_quotes('He said "alpha beta gamma') == []


def test_adjacent_quotes_extract_separately():
    assert extract_quotes('"alpha beta gamma" "delta epsilon zeta"') == [
        "alpha beta gamma",
        "delta epsilon zeta",
    ]


def test_empty_and_whitespace_quotes_are_skipped():
    assert extract_quotes('He said "" then "   " nothing') == []


def test_punctuation_only_quotes_are_skipped():
    assert extract_quotes('He said "—" and "…" loudly') == []


def test_punctuation_only_quotes_fail_the_gate():
    args = ["--source", SOURCE, "--answer", 'He said "…" here.', "--quotes", "--no-color"]
    assert verbatimeter.main(args) == 1


def test_duplicate_quotes_checked_once():
    assert extract_quotes('"alpha beta gamma" and again "alpha beta gamma"') == ["alpha beta gamma"]


def test_same_text_across_conventions_deduplicates():
    assert extract_quotes('"alpha beta gamma" et « alpha beta gamma »') == ["alpha beta gamma"]


def test_padded_curly_quotes_are_stripped_and_deduplicated():
    assert extract_quotes("He said “ alpha beta gamma ” with padding") == ["alpha beta gamma"]
    assert extract_quotes("“ alpha beta gamma ” and “alpha beta gamma”") == ["alpha beta gamma"]


def test_multiline_quote_extracts_and_matches():
    result = check_answer('"alpha\nbeta gamma" spans lines', SOURCE, scope="quotes")
    assert len(result.results) == 1
    assert result.results[0].matched_ratio == 1.0


def test_nested_quote_resolves_to_outermost():
    assert extract_quotes('Il dit « il a dit "beta gamma delta" hier » bon') == [
        'il a dit "beta gamma delta" hier'
    ]
    assert extract_quotes('He said "alpha « beta » gamma" ok') == ["alpha « beta » gamma"]


def test_nested_quote_inner_marks_do_not_break_matching():
    source = "il a dit beta gamma delta hier encore"
    result = check_answer('« il a dit "beta gamma delta" hier »', source, scope="quotes")
    assert result.results[0].matched_ratio == 1.0
    assert result.results[0].differing_tokens == 0


def test_short_quote_fails_closed():
    result = check_answer('The term "epsilon" appears', SOURCE, scope="quotes")
    assert len(result.results) == 1
    assert result.results[0].matched_ratio == 0.0
    args = ["--source", SOURCE, "--answer", 'The term "epsilon" appears', "--quotes", "--no-color"]
    assert verbatimeter.main(args) == 1


def test_inch_marks_are_not_quote_openers():
    assert extract_quotes("She is 5'4\" tall") == []
    assert extract_quotes('planks between 4" and 6" wide') == []
    assert extract_quotes('She is 5\'4" tall and said "alpha beta gamma" ok') == [
        "alpha beta gamma"
    ]
    assert extract_quotes('He said "alpha beta gamma" and is 5\'4" tall') == ["alpha beta gamma"]


def test_quote_ending_in_a_digit_still_extracts():
    assert extract_quotes('The abstract reports "achieves 28.4" exactly') == ["achieves 28.4"]


def test_mixed_good_and_bad_quotes_gate_on_any_failure():
    answer = '"alpha beta gamma" but also "omega psi chi"'
    result = check_answer(answer, SOURCE, scope="quotes")
    assert result.results[0].differing_tokens == 0
    assert result.results[1].differing_tokens > 0
    args = ["--source", SOURCE, "--answer", answer, "--quotes", "--no-color"]
    assert verbatimeter.main(args) == 1
