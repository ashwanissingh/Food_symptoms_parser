from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from lightparse.parsers.food import FoodParser
from lightparse.parsers.symptom import SymptomParser


@dataclass(frozen=True)
class LightParsePipeline:
    parser_version: str = "v1"

    def run(self, entry: dict[str, Any]) -> dict[str, Any]:
        entry_id = entry.get("entry_id")
        text = entry.get("text", "")

        output: dict[str, Any] = {
            "entry_id": entry_id,
            "foods": [],
            "symptoms": [],
            "parse_errors": [],
            "parser_version": self.parser_version,
        }

        if not entry_id:
            output["parse_errors"].append("missing_entry_id")
        if not isinstance(text, str):
            output["parse_errors"].append("invalid_text")
            text = ""

        try:
            output["foods"] = FoodParser.parse(text)
        except Exception as e:  # noqa: BLE001
            output["parse_errors"].append(f"food_parser_error:{type(e).__name__}")

        try:
            output["symptoms"] = SymptomParser.parse(text)
        except Exception as e:  # noqa: BLE001
            output["parse_errors"].append(f"symptom_parser_error:{type(e).__name__}")

        return output
