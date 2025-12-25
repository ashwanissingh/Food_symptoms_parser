# Light Parse (On‑Device, Deterministic) — Django + CLI

Light Parse is a **privacy-first**, **deterministic**, on-device journal parsing system.
It extracts only two categories of signals:

- **Foods** (FoodParser)
- **Physical symptoms** (SymptomParser)

Then a thin orchestrator combines both outputs (LightParsePipeline).

## Non-negotiable constraints

- **NO LLMs**
- **NO ML models**
- **NO cloud APIs**
- Only **rule-based parsing** (regex + small dictionaries/lexicons + simple heuristics)

This makes behavior auditable, testable, and safe to run on-device.

---

## Project structure

```
src/
  lightparse/
    parsers/
      food.py
      symptom.py
    pipeline/
      light_pipeline.py
    cli.py
  healthparse/         # minimal Django project
  ui/                  # Django UI app (no DB)
templates/
  base.html
  upload.html
  dashboard.html
  entry_detail.html
  components/
tests/
entries.jsonl          # sample upload file (JSONL)
```

---

## Architecture (mandatory separation)

### 1) FoodParser

- Public API: `FoodParser.parse(text) -> foods[]`
- Responsibility: **food extraction only**

Extracted fields per food:

- `name` (normalized singular when possible)
- `quantity` (optional)
- `unit` (optional)
- `meal` (`breakfast|lunch|dinner|snack|unknown`)
- `confidence` (0–1)

Rules include:

- Hinglish foods: `dal`, `chawal`, `idli`, `rajma`, `poha`, `paratha`, etc.
- Separators: `+`, `&`, commas, newlines
- Skipped meals detection: `Skipped dinner`, `Aaj dinner skip kiya`

### 2) SymptomParser

- Public API: `SymptomParser.parse(text) -> symptoms[]`
- Responsibility: **symptom extraction only** (physical)

Extracted fields per symptom:

- `name` (normalized)
- `severity` (optional, parsed from patterns like `6/10`)
- `time_hint` (optional: `morning|afternoon|evening|night|after_meal`)
- `negated` (true/false)
- `confidence` (0–1)

Rules include:

- Negation: `no headache`, `not bloated`, and post-negation hints like `(not now)`
- Ignores:
  - emotions (`mood`, `anxiety`)
  - vitals/metrics (`BP 120/80`, `steps 6234`)
  - medications
- No diagnosis inference

### 3) LightParsePipeline

- Public API: `LightParsePipeline.run(entry) -> combined_output`
- Runs both parsers and merges results into the required schema.

---

## Output format

For each entry:

```json
{
  "entry_id": "e_001",
  "foods": [],
  "symptoms": [],
  "parse_errors": [],
  "parser_version": "v1"
}
```

---

## CLI usage (no Django server required)

The CLI is exposed as `light_parse`.

```bash
light_parse --in entries.jsonl --out parsed.jsonl
```

- Input: JSONL, each line like `{ "entry_id": "e_001", "text": "..." }`
- Output: JSONL, one parsed object per input line

---

## Django UI (Upload → Dashboard → Entry Detail)

### Run the server

```bash
python src/manage.py runserver
```

### Pages

- `/upload/` — upload `entries.jsonl` and parse on-device
- `/dashboard/` — stats + table of entries
- `/entry/<entry_id>/` — raw text + foods/symptoms tables + confidence bars

### Storage (no database)

The UI stores parsed entries locally as JSONL:

- `data/parsed_store.jsonl`

Uploading a new file **upserts** by `entry_id`.

---

## Testing

```bash
pytest
```

Coverage includes:

- Negation
- Skipped meals
- Hinglish text
- False-positive numbers (BP/steps)
- Pipeline merge correctness

---

## Notes on the UI you may notice

- Some entries legitimately show **“No symptoms extracted”**.
  Example: `e_004` contains **anxiety**, which this system intentionally ignores (emotion, not a physical symptom).
- Meal may display as `-` when not explicitly inferable. This is intentional to avoid over-inference.

---

## Known limitations

- Deterministic lexicons are intentionally conservative: unknown foods/symptoms will be missed.
- Meal inference is keyword-driven; no probabilistic inference.
- Quantity/unit heuristics cover common patterns only.

---

## Future improvements

- Expand food/symptom lexicons via curated lists.
- Improve deterministic chunking for mixed-language entries.
- Add optional export from the UI (download parsed JSONL).
