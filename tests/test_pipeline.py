from lightparse.pipeline.light_pipeline import LightParsePipeline


def test_pipeline_combines_foods_and_symptoms() -> None:
    pipeline = LightParsePipeline(parser_version="v1")
    entry = {"entry_id": "e_001", "text": "2 eggs + 1 toast. Cramps started by noon"}
    out = pipeline.run(entry)

    assert out["entry_id"] == "e_001"
    assert out["parser_version"] == "v1"
    assert out["parse_errors"] == []

    food_names = {f["name"] for f in out["foods"]}
    symptom_names = {s["name"] for s in out["symptoms"]}

    assert "egg" in food_names
    assert "toast" in food_names
    assert "cramps" in symptom_names


def test_pipeline_missing_entry_id_is_reported() -> None:
    pipeline = LightParsePipeline(parser_version="v1")
    out = pipeline.run({"text": "chips. Stomach pain after 30 mins."})
    assert "missing_entry_id" in out["parse_errors"]
