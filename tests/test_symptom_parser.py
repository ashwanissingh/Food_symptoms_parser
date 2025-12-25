from lightparse.parsers.symptom import SymptomParser


def _names(items: list[dict]) -> set[str]:
    return {i["name"] for i in items}


def test_symptom_parser_negation_no_headache() -> None:
    symptoms = SymptomParser.parse("Skipped dinner. No headache today.")
    assert any(s["name"] == "headache" and s["negated"] is True for s in symptoms)


def test_symptom_parser_negation_parenthetical_not_now() -> None:
    symptoms = SymptomParser.parse("Slept late; headache next day (not now).")
    assert any(s["name"] == "headache" and s["negated"] is True for s in symptoms)


def test_symptom_parser_severity_and_time_hint() -> None:
    symptoms = SymptomParser.parse("paneer salad (1 bowl). Back pain 6/10 at night.")
    assert any(s["name"] == "back pain" and s["severity"] == 6 and s["time_hint"] == "night" for s in symptoms)


def test_symptom_parser_false_positive_numbers_are_ignored() -> None:
    symptoms = SymptomParser.parse("Felt dizzy, low energy. BP 120/80. Steps 6234")
    assert "dizziness" in _names(symptoms)
    assert "fatigue" in _names(symptoms)
    assert all(s["name"] not in {"bp", "steps", "weight"} for s in symptoms)


def test_symptom_parser_hinglish_time_hint_raat() -> None:
    symptoms = SymptomParser.parse("Raat ko cramps bahut zyada.")
    assert any(s["name"] == "cramps" and s["time_hint"] in {"evening", "night"} for s in symptoms)


def test_symptom_parser_ignores_emotions() -> None:
    symptoms = SymptomParser.parse("Mood a bit low. Anxiety spiked later.")
    assert symptoms == []
