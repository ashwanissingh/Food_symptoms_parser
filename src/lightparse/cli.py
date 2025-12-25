import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from lightparse.pipeline.light_pipeline import LightParsePipeline


def _read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                yield {"entry_id": None, "text": "", "_parse_error": f"json_decode_error_line_{line_num}:{e.msg}"}


def _write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False))
            f.write("\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="light_parse")
    parser.add_argument("--in", dest="in_path", required=True)
    parser.add_argument("--out", dest="out_path", required=True)
    args = parser.parse_args(argv)

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)

    pipeline = LightParsePipeline(parser_version="v1")

    outputs: list[dict[str, Any]] = []
    for entry in _read_jsonl(in_path):
        result = pipeline.run(entry)
        parse_err = entry.get("_parse_error")
        if parse_err:
            result["parse_errors"].append(parse_err)
        outputs.append(result)

    _write_jsonl(out_path, outputs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
