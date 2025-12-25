from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from lightparse.utils.text import normalize_whitespace, strip_non_text


_SEVERITY_RE = re.compile(r"\b(?P<sev>\d{1,2})\s*/\s*10\b")


_TIME_HINT_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("morning", re.compile(r"\bmorning\b|\bmid\-?morning\b|\bsubah\b", re.IGNORECASE)),
    ("afternoon", re.compile(r"\bafternoon\b", re.IGNORECASE)),
    ("evening", re.compile(r"\bevening\b|\bshaam\b|\braat\s+ko\b", re.IGNORECASE)),
    ("night", re.compile(r"\bnight\b|\braat\b", re.IGNORECASE)),
    ("after_meal", re.compile(r"\bafter\s+(?:eating|meal|lunch|dinner|breakfast)\b|\bpost\s+workout\b", re.IGNORECASE)),
]


_NEGATION_RE = re.compile(r"\b(?:no|not|without)\b", re.IGNORECASE)
_POST_NEGATION_HINTS = re.compile(r"\b(?:not\s+now|not\s+today|not\s+currently)\b", re.IGNORECASE)


_IGNORE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bbp\b\s*\d+\s*/\s*\d+", re.IGNORECASE),
    re.compile(r"\bsteps\b\s*\d+", re.IGNORECASE),
    re.compile(r"\bweight\b\s*\d+", re.IGNORECASE),
]


_SYMPTOM_LEXICON: dict[str, list[str]] = {
    "cramps": ["cramps", "cramp"],
    "bloating": ["bloated", "bloating"],
    "gas": ["gas", "gassy"],
    "headache": ["headache"],
    "migraine": ["migraine"],
    "back pain": ["back pain"],
    "stomach pain": ["stomach pain", "stomachache"],
    "fever": ["fever"],
    "dizziness": ["dizzy", "dizziness"],
    "fatigue": ["fatigue", "tired", "low energy"],
    "nausea": ["nausea", "nauseous"],
    "sore throat": ["sore throat"],
    "skin breakout": ["skin breakout", "breakout", "acne"],
    "jitteriness": ["jittery"],
    "palpitations": ["heart racing"],
    "sleepy": ["sleepy"],
    "heavy": ["felt heavy", "heavy"],
}


_EXCLUDED_TERMS = {
    "mood",
    "anxiety",
}


def _infer_time_hint(text: str) -> Optional[str]:
    for hint, pat in _TIME_HINT_PATTERNS:
        if pat.search(text):
            return hint
    return None


def _find_severity(text: str) -> Optional[int]:
    m = _SEVERITY_RE.search(text)
    if not m:
        return None
    try:
        sev = int(m.group("sev"))
    except ValueError:
        return None
    if 0 <= sev <= 10:
        return sev
    return None


def _is_negated(around_text: str) -> bool:
    if _NEGATION_RE.search(around_text):
        return True
    return bool(_POST_NEGATION_HINTS.search(around_text))


@dataclass(frozen=True)
class SymptomItem:
    name: str
    severity: Optional[int]
    time_hint: Optional[str]
    negated: bool
    confidence: float

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "severity": self.severity,
            "time_hint": self.time_hint,
            "negated": self.negated,
            "confidence": self.confidence,
        }


class SymptomParser:
    @classmethod
    def parse(cls, text: str) -> list[dict]:
        text = strip_non_text(text)
        lowered = text.lower()

        for pat in _IGNORE_PATTERNS:
            lowered = pat.sub(" ", lowered)

        severity = _find_severity(lowered)
        time_hint = _infer_time_hint(lowered)

        results: list[SymptomItem] = []

        for canonical, variants in _SYMPTOM_LEXICON.items():
            for v in sorted(variants, key=len, reverse=True):
                idx = lowered.find(v)
                if idx == -1:
                    continue

                left = max(0, idx - 30)
                right = min(len(lowered), idx + len(v) + 30)
                around = lowered[left:right]
                negated = _is_negated(around)

                confidence = 0.85
                if negated:
                    confidence = 0.95
                if severity is not None and canonical in {"migraine", "back pain", "headache", "cramps"}:
                    confidence = min(1.0, confidence + 0.05)

                results.append(
                    SymptomItem(
                        name=canonical,
                        severity=severity,
                        time_hint=time_hint,
                        negated=negated,
                        confidence=confidence,
                    )
                )

                lowered = lowered.replace(v, " ")

        cleaned = normalize_whitespace(lowered)
        for term in _EXCLUDED_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", cleaned):
                pass

        deduped: dict[tuple[str, bool, Optional[int], Optional[str]], SymptomItem] = {}
        for s in results:
            key = (s.name, s.negated, s.severity, s.time_hint)
            if key not in deduped or deduped[key].confidence < s.confidence:
                deduped[key] = s

        return [s.to_dict() for s in deduped.values()]
