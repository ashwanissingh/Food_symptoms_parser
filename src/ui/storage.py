import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Optional


@dataclass(frozen=True)
class StoredEntry:
    entry_id: str
    raw_text: str
    foods: list[dict[str, Any]]
    symptoms: list[dict[str, Any]]
    parse_errors: list[str]
    parser_version: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "raw_text": self.raw_text,
            "foods": self.foods,
            "symptoms": self.symptoms,
            "parse_errors": self.parse_errors,
            "parser_version": self.parser_version,
        }


def read_store(path: Path) -> list[StoredEntry]:
    if not path.exists():
        return []

    entries: list[StoredEntry] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_id = obj.get("entry_id")
            raw_text = obj.get("raw_text")
            if not entry_id or not isinstance(raw_text, str):
                continue

            entries.append(
                StoredEntry(
                    entry_id=str(entry_id),
                    raw_text=raw_text,
                    foods=list(obj.get("foods") or []),
                    symptoms=list(obj.get("symptoms") or []),
                    parse_errors=list(obj.get("parse_errors") or []),
                    parser_version=str(obj.get("parser_version") or "v1"),
                )
            )

    return entries


def write_store(path: Path, entries: Iterable[StoredEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e.to_dict(), ensure_ascii=False))
            f.write("\n")


def upsert_entries(path: Path, new_entries: Iterable[StoredEntry]) -> None:
    existing = read_store(path)
    by_id: dict[str, StoredEntry] = {e.entry_id: e for e in existing}

    for e in new_entries:
        by_id[e.entry_id] = e

    ordered = [by_id[k] for k in sorted(by_id.keys())]
    write_store(path, ordered)


def find_entry(path: Path, entry_id: str) -> Optional[StoredEntry]:
    for e in read_store(path):
        if e.entry_id == entry_id:
            return e
    return None
