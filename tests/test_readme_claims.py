import io
import json
from dataclasses import asdict
from pathlib import Path

import verbatimeter
from verbatimeter import check, check_answer, render_result
from verbatimeter.align import clean_text

DEMO_SOURCE = "\n\n".join(
    [
        "We propose a new simple network architecture, the Transformer, based solely on "
        "attention mechanisms, dispensing with recurrence and convolutions entirely.",
        "Experiments on two machine translation tasks show these models to be superior in "
        "quality while being more parallelizable and requiring significantly less time to train.",
        "We suspect that for large values of d_k, the dot products grow large in magnitude, "
        "pushing the softmax function into regions where it has extremely small gradients.",
        "Multi-head attention allows the model to jointly attend to information from different "
        "representation subspaces at different positions.",
    ]
)

DEMO_ANSWER = (
    "The paper proposes a new simple network architecture, the Transformer, based solely on "
    "attention mechanisms, dispensing with recurrence and convolutions entirely. It is faster "
    "to train because experiments show these models to be superior in quality while being more "
    "parallelizable and requiring significantly less time to train."
)

QUICKSTART_SOURCE = (
    "We propose a new simple network architecture, the Transformer, based solely on attention "
    "mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two "
    "machine translation tasks show these models to be superior in quality while being more "
    "parallelizable and requiring significantly less time to train."
)

QUICKSTART_ANSWER = (
    "We propose a new simple network architecture, the Transformer, based solely on attention "
    "mechanisms, dispensing with recurrence and convolutions entirely"
)


def test_pypi_badge_matches_the_package_version():
    badge = Path(__file__).parent.parent / "docs" / "assets" / "pypi-version-badge.svg"
    assert f"v{verbatimeter.__version__}" in badge.read_text(encoding="utf-8")


def test_same_inputs_produce_the_same_numbers_every_time():
    first = check(DEMO_ANSWER, DEMO_SOURCE)
    second = check(DEMO_ANSWER, DEMO_SOURCE)
    assert asdict(first) == asdict(second)
    third = check_answer(DEMO_ANSWER, DEMO_SOURCE, scope="all")
    fourth = check_answer(DEMO_ANSWER, DEMO_SOURCE, scope="all")
    assert asdict(third) == asdict(fourth)


def test_library_and_cli_numbers_are_identical(capsys):
    lib = check_answer(DEMO_ANSWER, DEMO_SOURCE)
    verbatimeter.main(["--source", DEMO_SOURCE, "--answer", DEMO_ANSWER, "--json"])
    cli = json.loads(capsys.readouterr().out)
    assert cli["results"][0]["matched_ratio"] == lib.results[0].matched_ratio
    assert cli["results"][0]["differing_tokens"] == lib.results[0].differing_tokens
    assert cli["results"][0]["total_tokens"] == lib.results[0].total_tokens
    assert cli["results"][0]["rouge_l"] == lib.results[0].rouge_l
    assert cli["total_differing_tokens"] == lib.total_differing_tokens


def test_demo_animation_numbers_reproduce():
    r = check(DEMO_ANSWER, DEMO_SOURCE)
    assert len(clean_text(DEMO_ANSWER)) == 47
    assert r.matched_ratio == 37 / 47
    assert [len(clean_text(f)) for f in r.fragments] == [18, 19]
    assert r.longest_fragment == 19
    assert r.differing_tokens == 10
    assert r.total_tokens == 55
    assert round(r.rouge_l, 3) == 0.844
    red = {w.text for w in r.words if w.verbatim is False}
    assert "experiments" in red


def test_quickstart_example_reports_full_match(capsys):
    code = verbatimeter.main(
        ["--source", QUICKSTART_SOURCE, "--answer", QUICKSTART_ANSWER, "--no-color"]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "matched=100%" in out
    assert "differing_tokens=0/" in out


def test_subsequence_mode_ignores_ngram():
    scrambled = "entirely convolutions and recurrence with dispensing"
    low = check(scrambled, QUICKSTART_SOURCE, mode="subsequence", ngram=3)
    high = check(scrambled, QUICKSTART_SOURCE, mode="subsequence", ngram=50)
    assert low.matched_ratio == high.matched_ratio
    assert low.fragments == high.fragments


def test_no_color_environment_variable_is_honored(monkeypatch):
    class Tty(io.StringIO):
        def isatty(self):
            return True

    monkeypatch.setenv("NO_COLOR", "1")
    result = check_answer("alpha beta gamma", "alpha beta gamma delta")
    rendered = render_result(result, stream=Tty())
    assert "matched=100%" in rendered
    assert "\033[" not in rendered


def test_custom_counter_never_touches_the_default_tokenizer(monkeypatch):
    from verbatimeter import core

    def boom():
        raise AssertionError("default tokenizer path used despite count_tokens")

    monkeypatch.setattr(core, "_bundled_cl100k_base", boom)
    r = check(DEMO_ANSWER, DEMO_SOURCE, count_tokens=lambda text: len(text.split()))
    assert r.total_tokens == len(DEMO_ANSWER.split())
    assert r.differing_tokens > 0
