"""Read the easy or complex optimization subset of Mamo."""

from pathlib import Path
from typing import Any

from ._loader import load_jsonl_records


class MamoManager:
    def __init__(
        self, dataset_path: str | None = None, difficulty: str = "easy"
    ) -> None:
        difficulty = difficulty.lower().strip()
        if difficulty not in {"easy", "complex"}:
            raise ValueError(
                f"Unknown difficulty: {difficulty}; expected easy or complex"
            )

        if dataset_path is None:
            project_root = Path(__file__).parent.parent.parent
            filename = (
                "Mamo_easy.jsonl" if difficulty == "easy" else "Mamo_complex.jsonl"
            )
            self.dataset_path = project_root / "benchmark" / filename
        else:
            self.dataset_path = Path(dataset_path)

        self._dataset = load_jsonl_records(self.dataset_path, ("id", "Question"))

    def _validate_index(self, index: int) -> None:
        if not (0 <= index < len(self._dataset)):
            raise IndexError(
                f"Index {index} is out of range [0, {len(self._dataset) - 1}]"
            )

    def _get_record(self, index: int) -> dict[str, Any]:
        self._validate_index(index)
        return self._dataset[index]

    def get_total_count(self) -> int:
        return len(self._dataset)

    def get_id(self, index: int) -> str:
        record = self._get_record(index)
        return str(record["id"])

    def get_input(self, index: int) -> str:
        record = self._get_record(index)
        question = record.get("Question")
        return str(question).strip() if question is not None else ""
