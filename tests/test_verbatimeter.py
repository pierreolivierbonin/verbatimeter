import io

import verbatimeter
from verbatimeter import (
    AnnotatedAnswer,
    CheckResult,
    check,
    check_answer,
    render_result,
    render_words,
    verify,
)
from verbatimeter.align import clean_text, contiguous_alignment, lcs_alignment

SOURCE = (
    "the attention mechanism computes a weighted sum of value vectors, where the "
    "weights are derived from the compatibility between a query and the corresponding keys"
)


def test_lcs_alignment():
    assert lcs_alignment(["a", "b", "c", "d"], ["a", "x", "c"]) == (2, [0, 2], [0, 2])
    assert lcs_alignment([], []) == (0, [], [])
    assert lcs_alignment(["a", "b", "c"], ["a", "b", "c"]) == (3, [0, 1, 2], [0, 1, 2])
    assert lcs_alignment(["a", "b"], ["x", "y"]) == (0, [], [])


def test_contiguous_alignment_ngram():
    ref = clean_text("the quick brown fox jumps")
    scattered = clean_text("the fox the brown")
    assert contiguous_alignment(ref, scattered) == ([], [])

    ref2 = clean_text("a b c d e")
    edited = clean_text("a b x d e")
    assert contiguous_alignment(ref2, edited, ngram=2)[1] == [0, 1, 3, 4]
    assert contiguous_alignment(ref2, edited)[1] == []


def test_clean_text_strips_unicode_punctuation():
    assert clean_text("employer’s") == clean_text("employer's") == ["employers"]
    assert clean_text("co—operate wait… re–enter") == ["cooperate", "wait", "reenter"]


def test_clean_text_normalizes_nfd_to_nfc():
    import unicodedata

    nfd = unicodedata.normalize("NFD", "café préavis employé")
    assert clean_text(nfd) == clean_text("café préavis employé")
    r = check(nfd, "café préavis employé")
    assert r.differing_tokens == 0
    assert r.matched_ratio == 1.0


def test_lcs_length_matches_full_alignment():
    from verbatimeter.align import _lcs_length

    cases = [
        (["a", "b", "c", "d"], ["a", "x", "c"]),
        ([], []),
        (["a", "b", "c"], ["a", "b", "c"]),
        (["a", "b"], ["x", "y"]),
        (["a", "b", "a", "b"], ["b", "a", "b", "a"]),
    ]
    for ref, cand in cases:
        assert _lcs_length(ref, cand) == lcs_alignment(ref, cand)[0]


def test_check_verbatim_excerpt_all_matched():
    r = check("the attention mechanism computes a weighted sum of value vectors", SOURCE)
    assert all(w.verbatim for w in r.words if w.verbatim is not None)
    assert r.differing_tokens == 0
    assert r.matched_ratio == 1.0


def test_check_smart_quote_is_not_a_difference():
    r = check("the compatibility between a query", "the compatibility between a query")
    assert r.differing_tokens == 0


def test_check_altered_words_flagged():
    r = check("the attention mechanism computes a weighted average of value vectors", SOURCE)
    red = {w.text for w in r.words if w.verbatim is False}
    assert "average" in red
    assert r.differing_tokens > 0
    assert r.matched_ratio < 1.0


def test_check_matches_across_the_whole_source():
    source = "alpha beta gamma delta\n\nepsilon zeta eta theta"
    r = check("alpha beta gamma and epsilon zeta eta", source)
    verbatim = {w.text for w in r.words if w.verbatim}
    assert "gamma" in verbatim and "epsilon" in verbatim
    assert r.matched_ratio == 6 / 7


def test_fragments_and_longest_run():
    r = check(
        "alpha beta gamma and epsilon zeta eta", "alpha beta gamma delta\n\nepsilon zeta eta theta"
    )
    assert r.fragments == ["alpha beta gamma", "epsilon zeta eta"]
    assert r.longest_fragment == 3


def test_fragments_tolerate_punctuation_only_tokens():
    r = check("alpha beta — gamma delta", "alpha beta gamma delta")
    assert r.fragments == ["alpha beta — gamma delta"]
    assert r.longest_fragment == 4


def test_segment_spans_all_matched_runs():
    source = "alpha beta gamma " + "filler " * 20 + "delta epsilon zeta"
    r = check("alpha beta gamma delta epsilon zeta", source)
    assert r.matched_ratio == 1.0
    assert r.source_segment.startswith("alpha")
    assert r.source_segment.endswith("zeta")


def test_ngram_threshold():
    source = "alpha beta gamma delta"
    assert check("beta gamma delta", source, ngram=3).matched_ratio == 1.0
    assert check("beta gamma delta", source, ngram=4).matched_ratio == 0.0


def test_ngram_floor_enforced():
    import pytest

    with pytest.raises(ValueError):
        check("beta gamma delta", "alpha beta gamma delta", ngram=2)


def test_contiguous_is_stricter_than_subsequence():
    source = "the quick brown fox jumps over the lazy dog"
    scrambled = "brown the fox lazy the quick"
    assert (
        check(scrambled, source).matched_ratio
        < check(scrambled, source, mode="subsequence").matched_ratio
    )


def test_scope_all_is_default_one_result():
    answer = 'It says "alpha beta gamma" then more.'
    result = check_answer(answer, "alpha beta gamma delta")
    assert result.scope == "all"
    assert len(result.results) == 1


def test_scope_quotes_extracts_each_span():
    answer = 'First "alpha beta gamma" then "epsilon zeta theta".'
    result = check_answer(
        answer, "alpha beta gamma delta\n\nepsilon zeta eta theta", scope="quotes"
    )
    assert len(result.results) == 2
    assert result.results[0].matched_ratio == 1.0
    assert result.results[1].matched_ratio == 0.0


def test_scope_quotes_extracts_curly_quotes():
    answer = 'First “alpha beta gamma” then "epsilon zeta eta".'
    result = check_answer(
        answer, "alpha beta gamma delta\n\nepsilon zeta eta theta", scope="quotes"
    )
    assert len(result.results) == 2
    assert result.results[0].text == "alpha beta gamma"
    assert result.results[0].matched_ratio == 1.0


def test_extract_quotes_guillemets_strip_inner_padding():
    from verbatimeter import extract_quotes

    assert extract_quotes("Il dit « alpha beta » puis « gamma delta ».") == [
        "alpha beta",
        "gamma delta",
    ]
    assert extract_quotes("Elle cite « epsilon zeta » ici.") == ["epsilon zeta"]


def test_extract_quotes_low9_and_mixed_conventions():
    from verbatimeter import extract_quotes

    answer = 'Er sagte „alpha beta“ then "gamma delta" et « epsilon zeta » and “eta theta”.'
    assert extract_quotes(answer) == [
        "alpha beta",
        "gamma delta",
        "epsilon zeta",
        "eta theta",
    ]


def test_render_no_color_and_color():
    r = CheckResult("all", [check("alpha beta gamma", "alpha beta gamma delta")])
    assert "\033[" not in render_result(r, use_color=False)
    words = check("alpha beta gamma unrelated words here", "alpha beta gamma delta").words
    out = render_words(words, use_color=True)
    assert "\033[32m" in out and "\033[31m" in out


def test_render_empty_messages():
    assert "No quotations" in render_result(CheckResult("quotes", []), use_color=False)
    assert "Empty input" in render_result(CheckResult("all", []), use_color=False)


def test_default_token_counting_is_offline(monkeypatch):
    import tiktoken

    from verbatimeter import core

    def boom(name):
        raise AssertionError("tiktoken.get_encoding called — default counter hit the network path")

    monkeypatch.setattr(tiktoken, "get_encoding", boom)
    core._bundled_cl100k_base.cache_clear()
    r = check("the attention mechanism computes a weighted average of value vectors", SOURCE)
    assert r.total_tokens > 0
    assert r.differing_tokens > 0


def test_bundled_encoding_matches_official_cl100k_base():
    import pytest
    import tiktoken

    from verbatimeter.core import _bundled_cl100k_base

    try:
        official = tiktoken.get_encoding("cl100k_base")
    except Exception as exc:
        pytest.skip(reason=f"official cl100k_base unavailable: {exc}")
    bundled = _bundled_cl100k_base()
    samples = [
        SOURCE,
        "We propose a new simple network architecture, the Transformer.",
        "employer’s co—operate wait… re–enter",
        "Chiffres 12345 → ponctuation!!! and\nnewlines\r\n\ttabs   spaces",
        "",
    ]
    for text in samples:
        assert bundled.encode(text) == official.encode(text)


def test_custom_tokenizer():
    words = lambda text: len(text.split())
    r = check("beta gamma delta unknownword", "alpha beta gamma delta", count_tokens=words)
    assert r.total_tokens == 4
    assert r.differing_tokens > 0


def test_decorator_static_source():
    sink = io.StringIO()

    @verify(source="alpha beta gamma delta", file=sink)
    def gen():
        return "alpha beta gamma"

    out = gen()
    assert out == "alpha beta gamma"
    assert isinstance(out, AnnotatedAnswer)
    assert out.result.total_differing_tokens == 0
    assert "matched" in sink.getvalue()


def test_decorator_quiet_mode_still_returns_result():
    sink = io.StringIO()

    @verify(source="alpha beta gamma delta", print_stats=False, file=sink)
    def gen():
        return "alpha beta gamma"

    out = gen()
    assert sink.getvalue() == ""
    assert isinstance(out, AnnotatedAnswer)
    assert out.result.total_differing_tokens == 0


def test_decorator_runtime_kwarg_wins():
    sink = io.StringIO()

    @verify(source="unrelated text here", source_arg="context", file=sink)
    def gen(context=None):
        return "alpha beta gamma delta"

    out = gen(context="alpha beta gamma delta epsilon")
    assert isinstance(out, AnnotatedAnswer)
    assert out.result.total_differing_tokens == 0


def test_decorator_positional_source_is_checked():
    sink = io.StringIO()

    @verify(source_arg="context", file=sink)
    def gen(prompt, context=None):
        return "alpha beta gamma"

    out = gen("q", "alpha beta gamma delta")
    assert isinstance(out, AnnotatedAnswer)
    assert out.result.total_differing_tokens == 0
    assert "matched" in sink.getvalue()


def test_decorator_file_output_has_no_ansi_when_stdout_is_tty(monkeypatch):
    import sys

    class Tty(io.StringIO):
        def isatty(self):
            return True

    monkeypatch.setattr(sys, "stdout", Tty())
    monkeypatch.delenv("NO_COLOR", raising=False)
    sink = io.StringIO()

    @verify(source="alpha beta gamma delta", file=sink)
    def gen():
        return "alpha beta gamma"

    gen()
    out = sink.getvalue()
    assert "matched" in out
    assert "\033[" not in out


def test_decorator_missing_source_is_noop():
    sink = io.StringIO()

    @verify(file=sink)
    def gen():
        return "anything"

    assert gen() == "anything"
    assert sink.getvalue() == ""


def test_cli_json_includes_computed_stats(capsys):
    import json

    verbatimeter.main(
        ["--source", "alpha beta gamma delta", "--answer", "alpha beta gamma", "--json"]
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["total_differing_tokens"] == 0
    assert payload["mean_rouge_l"] > 0
    assert payload["results"][0]["longest_fragment"] == 3


def test_cli_version(capsys):
    import pytest

    with pytest.raises(SystemExit) as exc:
        verbatimeter.main(["--version"])
    assert exc.value.code == 0
    assert verbatimeter.__version__ in capsys.readouterr().out


def test_cli_all_scope_never_gates(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("the employer shall provide written notice to each worker", encoding="utf-8")
    ans = tmp_path / "a.txt"
    ans.write_text("the employer must fabricate everything here", encoding="utf-8")
    args = ["--source", str(src), "--source-file", "--answer", str(ans), "--answer-file"]
    assert verbatimeter.main([*args, "--no-color"]) == 0


def test_cli_quotes_gate(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("the employer shall provide written notice to each worker", encoding="utf-8")
    good = tmp_path / "good.txt"
    good.write_text('It says "the employer shall provide written notice" here.', encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text('It says "the employer must provide verbal memos daily" here.', encoding="utf-8")
    base = ["--source", str(src), "--source-file", "--answer-file", "--quotes", "--no-color"]
    assert verbatimeter.main([*base, "--answer", str(good)]) == 0
    assert verbatimeter.main([*base, "--answer", str(bad)]) == 1
    assert verbatimeter.main([*base, "--answer", str(bad), "--no-fail"]) == 0


def test_cli_quotes_gate_fails_when_no_quotes_found(tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("the employer shall provide written notice to each worker", encoding="utf-8")
    unquoted = tmp_path / "unquoted.txt"
    unquoted.write_text("The employer shall provide written notice.", encoding="utf-8")
    args = [
        "--source",
        str(src),
        "--source-file",
        "--answer",
        str(unquoted),
        "--answer-file",
        "--quotes",
        "--no-color",
    ]
    assert verbatimeter.main(args) == 1
    assert verbatimeter.main([*args, "--no-fail"]) == 0


def test_cli_inputs_are_literal_without_file_flags(tmp_path, monkeypatch, capsys):
    import json

    trap = tmp_path / "answer.txt"
    trap.write_text("alpha beta gamma delta epsilon zeta eta theta", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    verbatimeter.main(["--source", "alpha beta gamma delta", "--answer", "answer.txt", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["results"][0]["text"] == "answer.txt"
