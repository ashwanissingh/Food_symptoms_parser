import re
from dataclasses import dataclass
from typing import Iterable


_WORD_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?", re.IGNORECASE)


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_non_text(text: str) -> str:
    text = text.replace("\u2019", "'")
    return text


def tokenize_words(text: str) -> list[str]:
    return [m.group(0).lower() for m in _WORD_RE.finditer(text)]


def split_on_separators(text: str) -> list[str]:
    text = text.replace("\n", ",")
    parts = re.split(r"\s*(?:\+|&|,|;|\band\b)\s*", text, flags=re.IGNORECASE)
    return [normalize_whitespace(p) for p in parts if normalize_whitespace(p)]


@dataclass(frozen=True)
class SpanMatch:
    value: str
    start: int
    end: int


def find_all(pattern: re.Pattern[str], text: str) -> list[SpanMatch]:
    matches: list[SpanMatch] = []
    for m in pattern.finditer(text):
        matches.append(SpanMatch(value=m.group(0), start=m.start(), end=m.end()))
    return matches


def any_keyword_in_text(keywords: Iterable[str], text: str) -> bool:
    t = text.lower()
    return any(k in t for k in keywords)
