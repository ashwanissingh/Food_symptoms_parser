On-Device Light Parsing — Food & Symptom Extraction

A privacy-first, deterministic parsing system that extracts structured food and symptom signals from free-text health journals — without using LLMs, ML models, or cloud services.

This project was built as part of Exercise C — On-Device Light Parsing and emphasizes clean system design, separation of concerns, and testability.

Overview

Daily health journals are often written in informal, mixed-language text.
This system converts such free-text entries into structured, machine-readable signals using rule-based parsing only, suitable for on-device execution.

Key principles:

Deterministic and explainable logic

Clear separation between food and symptom parsing

Conservative extraction (avoid over-parsing)

Easy to test, extend, and reason about

What This System Does

For each journal entry, the system extracts:

Food Signals

Normalized food name (singular form)

Optional quantity and unit

Meal type (breakfast / lunch / dinner / snack / unknown)

Confidence score (0–1)

Symptom Signals

Normalized symptom name

Optional severity (e.g., 6/10)

Optional time hint (morning, evening, after meal, etc.)

Negation flag (e.g., “no headache”)

Confidence score (0–1)

The final output is a structured JSON record per entry.

Architecture
Input (entries.jsonl)
        |
        v
┌────────────────────┐
│ LightParsePipeline │
│  (Orchestrator)    │
└──────┬───────┬─────┘
       │       │
       v       v
┌──────────┐ ┌────────────┐
│FoodParser│ │SymptomParser│
└──────────┘ └────────────┘
       │       │
       └───┬───┘
           v
     Parsed Output (JSONL)

Component Breakdown
1. FoodParser

Responsibility:
Extracts only food-related signals.

Key behaviors:

Normalizes plurals (e.g., eggs → egg)

Supports Hinglish foods (dal, chawal, idli, rajma, poha, etc.)

Handles informal separators (+, ,, &, newlines)

Detects skipped meals (e.g., “Skipped dinner”)

Does not infer nutrition, calories, or health impact

2. SymptomParser

Responsibility:
Extracts only physical symptom signals.

Key behaviors:

Handles symptom negation (“no headache”)

Extracts severity when explicitly stated (6/10)

Detects time hints (morning, night, after meal)

Ignores:

Emotions (mood, stress, anxiety unless clearly physical)

Vitals (BP, steps, weight)

Medications and diagnoses

3. LightParsePipeline

Responsibility:
A thin orchestrator that:

Runs FoodParser and SymptomParser independently

Merges results into a single structured output

Does not apply inference or transformation logic

Output Format

Each entry produces the following JSON structure:

{
  "entry_id": "e_012",
  "foods": [
    {
      "name": "chips",
      "quantity": null,
      "unit": null,
      "meal": "snack",
      "confidence": 0.7
    }
  ],
  "symptoms": [
    {
      "name": "stomach pain",
      "severity": null,
      "time_hint": "after_meal",
      "negated": false,
      "confidence": 0.8
    }
  ],
  "parse_errors": [],
  "parser_version": "v1"
}

CLI Usage

The system includes a CLI for batch processing.

light_parse --in entries.jsonl --out parsed.jsonl


Reads input as JSONL

Runs the parsing pipeline

Writes structured output as JSONL

Does not require running the Django server

Django UI

An optional Django UI is included for visualization.

Features:

Dark / black professional theme

Upload entries.jsonl

View parsed food & symptom results

Entry-level detail view

No cloud or external dependencies

Testing & Validation

Validation focuses on correctness and restraint.

Tests Included

Unit tests for FoodParser

Unit tests for SymptomParser

Integration tests for the pipeline

Covered Scenarios

Symptom negation

Skipped meals

Hinglish text

Severity extraction

False-positive numbers (BP, steps)

Evaluation Strategy

Synthetic dataset used as a golden reference

Priority given to precision over recall

Ambiguous cases are intentionally ignored

Key Assumptions

Journal entries are short and informal

Only explicitly stated signals should be extracted

Over-parsing is worse than missing weak signals

Deterministic rules are preferred over probabilistic inference

Known Limitations

Sarcasm or metaphorical language is not handled

Complex grammatical Hindi is only partially supported

Emoji interpretation is minimal

Confidence scores are heuristic, not learned

No cross-entry temporal reasoning

What Was Intentionally Not Done

No diagnosis inference

No emotion classification

No ML or LLM usage

No cloud APIs

No personalization or user profiling

Future Improvements

With more time, the system could be extended with:

Configurable lexicons (JSON/YAML)

Improved Hinglish normalization

Rule-explanation traces for debugging

Export to CSV / SQLite

Optional lightweight analytics on parsed outputs

Declaration

This project:

Is entirely my own work

Uses no prohibited tools or models

Follows the constraints and intent of Exercise C

Prioritizes clarity, determinism, and extensibility

Final Note

This project is designed to demonstrate system thinking, careful constraint handling, and clean architecture, rather than model complexity.
Every design choice favors explainability and correctness over cleverness.
