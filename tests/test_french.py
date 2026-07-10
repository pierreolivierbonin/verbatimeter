import verbatimeter
from verbatimeter import check, check_answer

FRENCH_SOURCE = (
    "L’employeur doit donner à l’employé un préavis de licenciement écrit d’au moins "
    "deux semaines avant la date du licenciement, sauf s’il lui verse une indemnité "
    "de départ équivalant à deux semaines de salaire au taux régulier"
)


def test_french_verbatim_excerpt_all_matched():
    r = check("un préavis de licenciement écrit d’au moins deux semaines", FRENCH_SOURCE)
    assert r.matched_ratio == 1.0
    assert r.differing_tokens == 0


def test_french_altered_word_flagged():
    r = check("un préavis de licenciement verbal d’au moins deux semaines", FRENCH_SOURCE)
    red = {w.text for w in r.words if w.verbatim is False}
    assert "verbal" in red
    assert r.differing_tokens > 0
    assert r.matched_ratio < 1.0


def test_french_apostrophe_variants_are_equivalent():
    typographic = "un préavis de licenciement écrit d’au moins deux semaines"
    ascii_variant = typographic.replace("’", "'")
    r = check(ascii_variant, FRENCH_SOURCE)
    assert r.matched_ratio == 1.0
    assert r.differing_tokens == 0


def test_french_guillemet_quotes_scope():
    answer = (
        "La loi exige « un préavis de licenciement écrit d’au moins deux semaines » "
        "mais elle invente aussi « une prime de rendement mensuelle obligatoire »."
    )
    result = check_answer(answer, FRENCH_SOURCE, scope="quotes")
    assert len(result.results) == 2
    assert result.results[0].matched_ratio == 1.0
    assert result.results[0].differing_tokens == 0
    assert result.results[1].matched_ratio == 0.0
    assert result.results[1].differing_tokens > 0


def test_french_cli_quotes_gate(tmp_path):
    src = tmp_path / "source.txt"
    src.write_text(FRENCH_SOURCE, encoding="utf-8")
    good = tmp_path / "good.txt"
    good.write_text(
        "Elle cite « une indemnité de départ équivalant à deux semaines de salaire » ici.",
        encoding="utf-8",
    )
    bad = tmp_path / "bad.txt"
    bad.write_text(
        "Elle cite « une indemnité de départ imposable au taux fédéral » ici.",
        encoding="utf-8",
    )
    base = ["--source-file", str(src), "--quotes", "--no-color"]
    assert verbatimeter.main([*base, "--answer-file", str(good), "--fail"]) == 0
    assert verbatimeter.main([*base, "--answer-file", str(bad)]) == 0
    assert verbatimeter.main([*base, "--answer-file", str(bad), "--fail"]) == 1
