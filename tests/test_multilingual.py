import pytest

import verbatimeter
from verbatimeter import check, check_answer

LANGUAGES = [
    pytest.param(
        "La biblioteca abre a las nueve de la mañana y cierra a las seis de la tarde.",
        "abre a las nueve de la mañana",
        "abre a las ocho de la mañana",
        "ocho",
        "El cartel dice «abre a las nueve de la mañana» en la entrada.",
        id="spanish",
    ),
    pytest.param(
        "A biblioteca abre às nove da manhã e fecha às seis da tarde.",
        "abre às nove da manhã",
        "abre às oito da manhã",
        "oito",
        "A placa diz «abre às nove da manhã» na entrada.",
        id="portuguese",
    ),
    pytest.param(
        "Die Bibliothek öffnet um neun Uhr morgens und schließt um sechs Uhr abends.",
        "öffnet um neun Uhr morgens",
        "öffnet um acht Uhr morgens",
        "acht",
        "Das Schild sagt „öffnet um neun Uhr morgens“ am Eingang.",
        id="german",
    ),
    pytest.param(
        "Библиотека открывается в девять часов утра и закрывается в шесть часов вечера.",
        "открывается в девять часов утра",
        "открывается в восемь часов утра",
        "восемь",
        "Табличка гласит «открывается в девять часов утра» у входа.",
        id="russian",
    ),
    pytest.param(
        "पुस्तकालय सुबह नौ बजे खुलता है और शाम छह बजे बंद होता है।",
        "सुबह नौ बजे खुलता है",
        "सुबह आठ बजे खुलता है",
        "आठ",
        "सूचना पट्ट पर लिखा है “सुबह नौ बजे खुलता है”।",
        id="hindi",
    ),
    pytest.param(
        "গ্রন্থাগার সকাল নয়টায় খোলে এবং সন্ধ্যা ছয়টায় বন্ধ হয়।",
        "সকাল নয়টায় খোলে",
        "সকাল আটটায় খোলে",
        "আটটায়",
        "নোটিশে লেখা আছে “সকাল নয়টায় খোলে”।",
        id="bengali",
    ),
    pytest.param(
        "Perpustakaan buka pukul sembilan pagi dan tutup pukul enam sore.",
        "buka pukul sembilan pagi",
        "buka pukul delapan pagi",
        "delapan",
        "Papan itu bertuliskan “buka pukul sembilan pagi” di pintu masuk.",
        id="indonesian",
    ),
    pytest.param(
        "تفتح المكتبة أبوابها في الساعة التاسعة صباحا وتغلق في الساعة السادسة مساء",
        "في الساعة التاسعة صباحا وتغلق",
        "في الساعة الثامنة صباحا وتغلق",
        "الثامنة",
        "مكتوب هنا «في الساعة التاسعة صباحا وتغلق» فقط.",
        id="arabic",
    ),
    pytest.param(
        "کتب خانہ صبح نو بجے کھلتا ہے اور شام چھ بجے بند ہوتا ہے۔",
        "صبح نو بجے کھلتا ہے",
        "صبح آٹھ بجے کھلتا ہے",
        "آٹھ",
        "بورڈ پر لکھا ہے “صبح نو بجے کھلتا ہے”۔",
        id="urdu",
    ),
]


@pytest.mark.parametrize("source, excerpt, altered, red_word, quoted", LANGUAGES)
def test_verbatim_excerpt_matches(source, excerpt, altered, red_word, quoted):
    r = check(excerpt, source)
    assert r.matched_ratio == 1.0
    assert r.differing_tokens == 0


@pytest.mark.parametrize("source, excerpt, altered, red_word, quoted", LANGUAGES)
def test_altered_word_flagged(source, excerpt, altered, red_word, quoted):
    r = check(altered, source)
    red = {w.text for w in r.words if w.verbatim is False}
    assert red_word in red
    assert r.differing_tokens > 0
    assert r.matched_ratio < 1.0


@pytest.mark.parametrize("source, excerpt, altered, red_word, quoted", LANGUAGES)
def test_native_quote_convention(source, excerpt, altered, red_word, quoted):
    result = check_answer(quoted, source, scope="quotes")
    assert len(result.results) == 1
    assert result.results[0].matched_ratio == 1.0
    assert result.results[0].differing_tokens == 0


def test_casefold_sharp_s_and_uppercase_cyrillic():
    german = "Die Bibliothek öffnet um neun Uhr morgens und schließt um sechs Uhr abends."
    r = check("SCHLIESST UM SECHS UHR ABENDS", german)
    assert r.matched_ratio == 1.0
    russian = "Библиотека открывается в девять часов утра и закрывается в шесть часов вечера."
    r2 = check("ОТКРЫВАЕТСЯ В ДЕВЯТЬ ЧАСОВ УТРА", russian)
    assert r2.matched_ratio == 1.0


def test_cli_quotes_gate_arabic(tmp_path):
    src = tmp_path / "source.txt"
    src.write_text(
        "تفتح المكتبة أبوابها في الساعة التاسعة صباحا وتغلق في الساعة السادسة مساء",
        encoding="utf-8",
    )
    good = tmp_path / "good.txt"
    good.write_text("مكتوب هنا «في الساعة التاسعة صباحا وتغلق» فقط.", encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("مكتوب هنا «تفتح يوم الأحد بعد الظهر» فقط.", encoding="utf-8")
    base = ["--source-file", str(src), "--quotes", "--no-color"]
    assert verbatimeter.main([*base, "--answer-file", str(good), "--fail"]) == 0
    assert verbatimeter.main([*base, "--answer-file", str(bad), "--fail"]) == 1


def test_cli_quotes_gate_hindi(tmp_path):
    src = tmp_path / "source.txt"
    src.write_text("पुस्तकालय सुबह नौ बजे खुलता है और शाम छह बजे बंद होता है।", encoding="utf-8")
    good = tmp_path / "good.txt"
    good.write_text("सूचना पट्ट पर लिखा है “सुबह नौ बजे खुलता है”।", encoding="utf-8")
    bad = tmp_path / "bad.txt"
    bad.write_text("सूचना पट्ट पर लिखा है “दोपहर बारह बजे बंद रहता है”।", encoding="utf-8")
    base = ["--source-file", str(src), "--quotes", "--no-color"]
    assert verbatimeter.main([*base, "--answer-file", str(good), "--fail"]) == 0
    assert verbatimeter.main([*base, "--answer-file", str(bad), "--fail"]) == 1
