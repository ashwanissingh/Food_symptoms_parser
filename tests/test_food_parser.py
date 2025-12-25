import pytest

from lightparse.parsers.food import FoodParser


def _names(items: list[dict]) -> set[str]:
    return {i["name"] for i in items}


def test_food_parser_basic_breakfast_separators_and_plural_normalization() -> None:
    foods = FoodParser.parse("2 eggs + 1 toast for breakfast")
    assert "egg" in _names(foods)
    assert "toast" in _names(foods)
    assert any(f["name"] == "egg" and f["quantity"] == "2" for f in foods)


def test_food_parser_skipped_meal_english_and_hinglish() -> None:
    foods1 = FoodParser.parse("Skipped dinner. No headache today.")
    assert any(f["name"] == "skipped_meal" and f["meal"] == "dinner" for f in foods1)

    foods2 = FoodParser.parse("Aaj dinner skip kiya. Raat ko cramps bahut zyada.")
    assert any(f["name"] == "skipped_meal" and f["meal"] == "dinner" for f in foods2)


def test_food_parser_hinglish_embedded_phrase_with_qty_after_name() -> None:
    foods = FoodParser.parse("Aaj lunch mein rajma chawal, 1 plate. Gas + bloating in evening.")
    assert "rajma" in _names(foods)
    assert "chawal" in _names(foods)


def test_food_parser_does_not_emit_symptoms_as_foods() -> None:
    foods = FoodParser.parse("Cramps started by noon")
    assert foods == []
