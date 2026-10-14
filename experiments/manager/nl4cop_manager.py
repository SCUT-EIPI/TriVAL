"""Read NL4COP problem files in problem_id order."""

import json
from pathlib import Path
from typing import Any


class NL4COPManager:
    def __init__(self, dataset_path: str | None = None) -> None:
        if dataset_path is None:
            project_root = Path(__file__).parent.parent.parent
            self.dataset_path = project_root / "benchmark" / "NL4COP"
        else:
            self.dataset_path = Path(dataset_path)

        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self.dataset_path}")

        self._dataset = self._load_data()

    def _load_data(self) -> list[dict[str, Any]]:
        """Load JSON records and sort them by problem_id."""
        problems: list[dict[str, Any]] = []

        json_files = sorted(self.dataset_path.glob("*.json"))

        for file_path in json_files:
            try:
                with open(file_path, encoding="utf-8") as f:
                    problem_data: dict[str, Any] = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(
                    f"Invalid JSON in {file_path}: {e.msg}", e.doc, e.pos
                ) from e

            if not isinstance(problem_data, dict):
                raise ValueError(f"Expected a JSON object in {file_path}")

            problem_id = problem_data.get("problem_id") or Path(file_path).stem
            problem_data["problem_id"] = problem_id
            problems.append(problem_data)

        problems.sort(key=lambda item: item["problem_id"])
        if not problems:
            raise ValueError(f"Dataset is empty: {self.dataset_path}")
        return problems

    def _validate_index(self, index: int) -> None:
        if not (0 <= index < len(self._dataset)):
            raise IndexError(
                f"Index {index} is out of range [0, {len(self._dataset) - 1}]"
            )

    def get_total_count(self) -> int:
        return len(self._dataset)

    def get_id(self, index: int) -> str:
        self._validate_index(index)
        return str(self._dataset[index]["problem_id"])

    def get_input(self, index: int) -> str:
        self._validate_index(index)
        problem = self._dataset[index]

        description = problem.get("problem_description")
        return str(description).strip() if description is not None else ""
