"""Read the prepared OptiBench benchmark."""

from pathlib import Path
from typing import Any

from ._loader import load_jsonl_records


class OptiBenchManager:
    def __init__(self, dataset_path: str | None = None) -> None:
        if dataset_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.dataset_path = project_root / "benchmark" / "OptiBench.jsonl"
        else:
            self.dataset_path = Path(dataset_path)

        self._dataset = load_jsonl_records(
            self.dataset_path, ("id", "question", "results")
        )

    def _validate_index(self, index: int) -> None:
        if not (0 <= index < len(self._dataset)):
            raise IndexError(
                f"Index {index} is out of range; dataset size: {len(self._dataset)}"
            )

    def _get_record(self, index: int) -> dict[str, Any]:
        self._validate_index(index)
        return self._dataset[index]

    def get_total_count(self) -> int:
        return len(self._dataset)

    def get_id(self, index: int) -> str:
        record = self._get_record(index)
        return str(record["id"]).strip()

    def get_input(self, index: int) -> str:
        record = self._get_record(index)
        question = record.get("question")
        return str(question).strip() if question is not None else ""
