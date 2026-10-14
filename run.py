"""Run TriVAL on one dataset record or one text file."""

import argparse
from pathlib import Path

from agents.core import get_llm
from agents.runner import run_trival
from agents.schema import ContextSchema
from experiments.manager import (
    IndustryORManager,
    MamoManager,
    NL4COPManager,
    NL4LPManager,
    NL4OptManager,
    OptiBenchManager,
    OptmathManager,
)

DATASET_MANAGERS = {
    "industryor": IndustryORManager,
    "mamo_easy": lambda: MamoManager(difficulty="easy"),
    "mamo_complex": lambda: MamoManager(difficulty="complex"),
    "nl4cop": NL4COPManager,
    "nl4lp": NL4LPManager,
    "nl4opt": NL4OptManager,
    "optibench": OptiBenchManager,
    "optmath": OptmathManager,
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model", default="deepseek-flash", help="DeepSeek model identifier."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dataset", choices=sorted(DATASET_MANAGERS))
    source.add_argument(
        "--file", type=Path, help="UTF-8 text file containing one problem."
    )
    parser.add_argument(
        "--index", type=int, help="Zero-based record index; required with --dataset."
    )
    args = parser.parse_args(argv)
    if args.dataset and args.index is None:
        parser.error("--dataset requires --index")
    if args.file and args.index is not None:
        parser.error("--index can only be used with --dataset")
    if args.index is not None and args.index < 0:
        parser.error("--index must be non-negative")
    return args


def load_problem_description(args) -> str:
    if args.file:
        problem_description = args.file.read_text(encoding="utf-8").strip()
    else:
        manager = DATASET_MANAGERS[args.dataset]()
        problem_description = manager.get_input(args.index)
    if not problem_description.strip():
        raise ValueError("The problem description is empty.")
    return problem_description


def main() -> int:
    args = parse_args()
    try:
        problem_description = load_problem_description(args)
    except (OSError, UnicodeError, ValueError, IndexError, KeyError) as exc:
        raise SystemExit(str(exc)) from exc
    context = ContextSchema(llm=get_llm(args.model))
    result = run_trival(problem_description=problem_description, context=context)
    print("\n=== Generated Code ===")
    print(result.get("code") or "(no generated code)")
    print("\n=== Execution Feedback ===")
    print(result.get("execution_feedback") or "(no execution feedback)")
    return (
        0
        if result.get("code_executable") and result.get("code_validation_passed")
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
