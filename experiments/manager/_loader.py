import json
from pathlib import Path


def load_jsonl_records(
    dataset_path: Path, required_fields: tuple[str, ...]
) -> list[dict]:
    records = []
    with dataset_path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise json.JSONDecodeError(
                    f"Invalid JSON in {dataset_path} on line {line_number}: {exc.msg}",
                    exc.doc,
                    exc.pos,
                ) from exc
            if not isinstance(record, dict):
                raise ValueError(
                    f"Expected a JSON object in {dataset_path} on line {line_number}"
                )
            missing = set(required_fields) - record.keys()
            if missing:
                raise KeyError(
                    f"Missing required fields {missing} at line {line_number}"
                )
            records.append(record)
    if not records:
        raise ValueError(f"Dataset is empty: {dataset_path}")
    return records
