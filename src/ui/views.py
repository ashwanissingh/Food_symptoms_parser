from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from lightparse.pipeline.light_pipeline import LightParsePipeline
from ui.storage import StoredEntry, find_entry, upsert_entries, read_store


def _store_path() -> Path:
    return Path(settings.LIGHTPARSE_STORE_PATH)


def upload_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        f = request.FILES.get("file")
        if not f:
            messages.error(request, "No file selected")
            return redirect("upload")

        if not f.name.endswith(".jsonl"):
            messages.error(request, "Invalid file type. Please upload a .jsonl file")
            return redirect("upload")

        pipeline = LightParsePipeline(parser_version="v1")
        new_entries: list[StoredEntry] = []

        try:
            content = f.read().decode("utf-8")
        except Exception:  # noqa: BLE001
            messages.error(request, "Could not read file")
            return redirect("upload")

        for idx, line in enumerate(content.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue

            entry_id = obj.get("entry_id")
            text = obj.get("text", "")
            if not entry_id or not isinstance(text, str):
                continue

            parsed = pipeline.run({"entry_id": entry_id, "text": text})
            new_entries.append(
                StoredEntry(
                    entry_id=str(entry_id),
                    raw_text=text,
                    foods=list(parsed.get("foods") or []),
                    symptoms=list(parsed.get("symptoms") or []),
                    parse_errors=list(parsed.get("parse_errors") or []),
                    parser_version=str(parsed.get("parser_version") or "v1"),
                )
            )

        if not new_entries:
            messages.error(request, "No valid entries found in file")
            return redirect("upload")

        upsert_entries(_store_path(), new_entries)
        messages.success(request, f"Parsed {len(new_entries)} entries")
        return redirect("dashboard")

    return render(request, "upload.html")


def dashboard_view(request: HttpRequest) -> HttpResponse:
    entries = read_store(_store_path())

    total = len(entries)
    food_count = sum(1 for e in entries if len(e.foods) > 0)
    symptom_count = sum(1 for e in entries if len(e.symptoms) > 0)
    negated = 0
    for e in entries:
        for s in e.symptoms:
            if s.get("negated") is True:
                negated += 1

    def _with_confidence_pct(entry: dict[str, Any]) -> dict[str, Any]:
        foods = []
        for f in list(entry.get("foods") or []):
            f2 = dict(f)
            try:
                f2["confidence_pct"] = int(float(f2.get("confidence") or 0.0) * 100)
            except (TypeError, ValueError):
                f2["confidence_pct"] = 0
            foods.append(f2)

        symptoms = []
        for s in list(entry.get("symptoms") or []):
            s2 = dict(s)
            try:
                s2["confidence_pct"] = int(float(s2.get("confidence") or 0.0) * 100)
            except (TypeError, ValueError):
                s2["confidence_pct"] = 0
            symptoms.append(s2)

        entry2 = dict(entry)
        entry2["foods"] = foods
        entry2["symptoms"] = symptoms
        return entry2

    context: dict[str, Any] = {
        "entries": [_with_confidence_pct(e.to_dict()) for e in entries],
        "total": total,
        "food_count": food_count,
        "symptom_count": symptom_count,
        "negated": negated,
    }
    return render(request, "dashboard.html", context)


def entry_detail_view(request: HttpRequest, entry_id: str) -> HttpResponse:
    e = find_entry(_store_path(), entry_id)
    if not e:
        messages.error(request, f"Entry not found: {entry_id}")
        return redirect("dashboard")

    entry_dict = e.to_dict()
    foods = []
    for f in list(entry_dict.get("foods") or []):
        f2 = dict(f)
        try:
            f2["confidence_pct"] = int(float(f2.get("confidence") or 0.0) * 100)
        except (TypeError, ValueError):
            f2["confidence_pct"] = 0
        foods.append(f2)

    symptoms = []
    for s in list(entry_dict.get("symptoms") or []):
        s2 = dict(s)
        try:
            s2["confidence_pct"] = int(float(s2.get("confidence") or 0.0) * 100)
        except (TypeError, ValueError):
            s2["confidence_pct"] = 0
        symptoms.append(s2)

    entry_dict["foods"] = foods
    entry_dict["symptoms"] = symptoms

    context: dict[str, Any] = {
        "entry": entry_dict,
    }
    return render(request, "entry_detail.html", context)
