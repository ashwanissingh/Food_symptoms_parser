from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from lightparse.utils.text import normalize_whitespace, split_on_separators, strip_non_text


_MEAL_KEYWORDS = {
    "breakfast": ["breakfast", "bf"],
    "lunch": ["lunch"],
    "dinner": ["dinner"],
    "snack": ["snack", "snacks"],
}


_HINGLISH_MEAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("lunch", re.compile(r"\baaj\s+lunch\b|\blunch\s+mein\b", re.IGNORECASE)),
    ("dinner", re.compile(r"\baaj\s+dinner\b|\bdinner\s+mein\b", re.IGNORECASE)),
]


_SKIPPED_MEAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("breakfast", re.compile(r"\bskipp?ed\s+breakfast\b|\bbreakfast\s+skip\b", re.IGNORECASE)),
    ("lunch", re.compile(r"\bskipp?ed\s+lunch\b|\blunch\s+skip\b", re.IGNORECASE)),
    ("dinner", re.compile(r"\bskipp?ed\s+dinner\b|\bdinner\s+skip\b|\bdinner\s+skip\s+kiya\b|\baaj\s+dinner\s+skip\s+kiya\b", re.IGNORECASE)),
]


_UNIT_RE = r"(?:cup|cups|bowl|bowls|plate|plates|slice|slices|piece|pieces)"
_QUANTITY_RE = r"(?:\d+(?:\.\d+)?|half|1/2)"

_QTY_UNIT_PREFIX = re.compile(
    rf"\b(?P<qty>{_QUANTITY_RE})\s*(?P<unit>{_UNIT_RE})?\b\s*(?P<name>[a-z][a-z\s\-']+)\b",
    re.IGNORECASE,
)

_QTY_IN_PARENS = re.compile(
    r"\((?P<qty>\d+(?:\.\d+)?)\s*(?P<unit>" + _UNIT_RE + r")?\)",
    re.IGNORECASE,
)

_NAME_THEN_QTY_UNIT = re.compile(
    rf"\b(?P<name>[a-z][a-z\s\-']+?)\b\s*(?P<qty>{_QUANTITY_RE})\s*(?P<unit>{_UNIT_RE})\b",
    re.IGNORECASE,
)

_FRAGMENT_STOPWORDS = {
    "had",
    "have",
    "ate",
    "for",
    "with",
    "and",
    "at",
    "my",
    "favorite",
    "restaurant",
    "mein",
    "aaj",
    "lunch",
    "dinner",
    "breakfast",
    "snack",
    "post",
    "workout",
}


_FOOD_LEXICON = {
    "egg",
    "toast",
    "dal",
    "chawal",
    "dahi",
    "banana",
    "almond",
    "paneer",
    "salad",
    "coffee",
    "oats",
    "milk",
    "sushi",
    "pizza",
    "diet coke",
    "coke",
    "rajma",
    "idli",
    "sambar",
    "chai",
    "chips",
    "khichdi",
    "protein shake",
    "poha",
    "chicken wrap",
    "wrap",
    "fish curry",
    "rice",
    "cookie",
    "tea",
    "sugar",
    "yogurt",
    "berries",
    "moong dal dosa",
    "dosa",
    "chutney",
    "avocado",
    "pasta",
    "white sauce",
    "chocolate",
    "ice cream",
    "paratha",
    "curd",
    "egg biryani",
    "biryani",
}


_MULTIWORD_FOODS = sorted([f for f in _FOOD_LEXICON if " " in f], key=len, reverse=True)


def _singularize(name: str) -> str:
    name = name.strip()
    if name.endswith("ies") and len(name) > 4:
        return name[:-3] + "y"
    if name.endswith("s") and not name.endswith("ss") and len(name) > 3:
        return name[:-1]
    return name


def _normalize_food_name(raw: str) -> str:
    n = normalize_whitespace(raw.lower())
    n = re.sub(r"[^a-z0-9\s\-']", "", n)
    n = normalize_whitespace(n)

    if n in {"diet coke", "coke"}:
        return "diet coke" if "diet" in n else "coke"

    n = _singularize(n)
    return n


def _detect_meal(text: str) -> str:
    t = text.lower()

    for meal, kws in _MEAL_KEYWORDS.items():
        for kw in kws:
            if re.search(rf"\b{re.escape(kw)}\b", t):
                return meal

    for meal, pat in _HINGLISH_MEAL_PATTERNS:
        if pat.search(text):
            return meal

    return "unknown"


def _extract_known_foods(fragment: str) -> list[str]:
    """Extract foods from a fragment by lexicon matching only.

    This intentionally avoids free-form NLP and only returns items found in the
    fixed lexicon.
    """

    f = normalize_whitespace(fragment.lower())
    f = re.sub(r"[^a-z0-9\s\-']", " ", f)
    f = normalize_whitespace(f)
    if not f:
        return []

    found: list[str] = []

    for phrase in _MULTIWORD_FOODS:
        if re.search(rf"\b{re.escape(phrase)}\b", f):
            found.append(_normalize_food_name(phrase))
            f = re.sub(rf"\b{re.escape(phrase)}\b", " ", f)
            f = normalize_whitespace(f)

    tokens = [t for t in f.split(" ") if t and t not in _FRAGMENT_STOPWORDS]
    for t in tokens:
        n = _normalize_food_name(t)
        if n in _FOOD_LEXICON:
            found.append(n)

    return found


@dataclass(frozen=True)
class FoodItem:
    name: str
    quantity: Optional[str]
    unit: Optional[str]
    meal: str
    confidence: float

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "meal": self.meal,
            "confidence": self.confidence,
        }


class FoodParser:
    @classmethod
    def parse(cls, text: str) -> list[dict]:
        text = strip_non_text(text)
        meal = _detect_meal(text)
        foods: list[FoodItem] = []

        for skipped_meal, pat in _SKIPPED_MEAL_PATTERNS:
            if pat.search(text):
                foods.append(
                    FoodItem(
                        name="skipped_meal",
                        quantity=None,
                        unit=None,
                        meal=skipped_meal,
                        confidence=1.0,
                    )
                )

        lowered = text.lower()
        for phrase in _MULTIWORD_FOODS:
            if phrase in lowered:
                foods.append(
                    FoodItem(
                        name=_normalize_food_name(phrase),
                        quantity=None,
                        unit=None,
                        meal=meal,
                        confidence=0.85,
                    )
                )
                lowered = lowered.replace(phrase, " ")

        parts = split_on_separators(lowered)
        for part in parts:
            if not part:
                continue

            part = normalize_whitespace(part)
            if not part:
                continue

            m2 = _NAME_THEN_QTY_UNIT.search(part)
            if m2:
                name = _normalize_food_name(m2.group("name"))
                qty = m2.group("qty")
                unit = m2.group("unit")
                if name in _FOOD_LEXICON:
                    foods.append(
                        FoodItem(
                            name=name,
                            quantity=qty,
                            unit=unit.lower() if unit else None,
                            meal=meal,
                            confidence=0.85,
                        )
                    )
                    continue

            m = _QTY_UNIT_PREFIX.search(part)
            if m:
                qty = m.group("qty")
                unit = m.group("unit")
                raw_name = m.group("name")
                name = _normalize_food_name(raw_name)
                if name in _FOOD_LEXICON:
                    foods.append(
                        FoodItem(
                            name=name,
                            quantity=qty,
                            unit=unit.lower() if unit else None,
                            meal=meal,
                            confidence=0.9,
                        )
                    )
                    continue

            par = _QTY_IN_PARENS.search(part)
            par_qty = par.group("qty") if par else None
            par_unit = par.group("unit") if par else None
            cleaned = re.sub(r"\([^)]*\)", " ", part)
            cleaned = normalize_whitespace(cleaned)

            if cleaned in _FOOD_LEXICON:
                foods.append(
                    FoodItem(
                        name=_normalize_food_name(cleaned),
                        quantity=par_qty,
                        unit=par_unit.lower() if par_unit else None,
                        meal=meal,
                        confidence=0.8,
                    )
                )
                continue

            cleaned = _normalize_food_name(cleaned)
            if cleaned in _FOOD_LEXICON:
                foods.append(
                    FoodItem(
                        name=cleaned,
                        quantity=par_qty,
                        unit=par_unit.lower() if par_unit else None,
                        meal=meal,
                        confidence=0.75,
                    )
                )

            if cleaned not in _FOOD_LEXICON:
                for name in _extract_known_foods(part):
                    foods.append(
                        FoodItem(
                            name=name,
                            quantity=par_qty,
                            unit=par_unit.lower() if par_unit else None,
                            meal=meal,
                            confidence=0.7,
                        )
                    )

        deduped: dict[tuple[str, str, Optional[str], Optional[str]], FoodItem] = {}
        for f in foods:
            key = (f.name, f.meal, f.quantity, f.unit)
            if key not in deduped or deduped[key].confidence < f.confidence:
                deduped[key] = f

        return [f.to_dict() for f in deduped.values()]
