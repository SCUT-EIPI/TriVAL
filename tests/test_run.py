import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run
from agents.core.llm import get_llm
from agents.graph import create_trival_graph


class SingleProblemTests(unittest.TestCase):
    def test_dataset_input_contains_only_the_problem_description(self):
        path = Path(__file__).resolve().parents[1] / "benchmark" / "NL4COP"
        record = json.loads(sorted(path.glob("*.json"))[0].read_text())
        args = run.parse_args(["--dataset", "nl4cop", "--index", "0"])
        self.assertEqual(
            run.load_problem_description(args), record["problem_description"].strip()
        )

    def test_file_input_and_empty_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "problem.txt"
            args = run.parse_args(["--file", str(path)])
            path.write_text("  Maximize profit.\n", encoding="utf-8")
            self.assertEqual(run.load_problem_description(args), "Maximize profit.")
            path.write_text(" \n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "empty"):
                run.load_problem_description(args)

    def test_invalid_input_combinations(self):
        cases = [
            [],
            ["--dataset", "nl4cop"],
            ["--dataset", "nl4cop", "--index", "-1"],
            ["--file", "problem.txt", "--index", "0"],
            ["--file", "problem.txt", "--dataset", "nl4cop"],
        ]
        for argv in cases:
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as error:
                    run.parse_args(argv)
                self.assertEqual(error.exception.code, 2)

    def test_all_datasets_load_and_reject_out_of_range_indices(self):
        for name, factory in run.DATASET_MANAGERS.items():
            with self.subTest(dataset=name):
                manager = factory()
                count = manager.get_total_count()
                ids = [manager.get_id(i) for i in range(count)]
                self.assertEqual(len(ids), len(set(ids)))
                self.assertTrue(all(manager.get_input(i).strip() for i in range(count)))
                with self.assertRaises(IndexError):
                    manager.get_input(count)

    def test_main_runs_one_problem_with_the_selected_deepseek_model(self):
        args = [
            "run.py",
            "--model",
            "deepseek-v4-pro",
            "--dataset",
            "nl4cop",
            "--index",
            "0",
        ]
        result = {
            "code": "print('solution')",
            "execution_feedback": "solution",
            "code_executable": True,
            "code_validation_passed": True,
        }
        with (
            patch("sys.argv", args),
            patch("run.get_llm") as model,
            patch("run.run_trival", return_value=result) as agent,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(run.main(), 0)
        model.assert_called_once_with("deepseek-v4-pro")
        agent.assert_called_once()
        self.assertEqual(
            set(agent.call_args.kwargs), {"problem_description", "context"}
        )
        self.assertEqual(set(agent.call_args.kwargs["context"]), {"llm"})

    def test_main_rejects_executable_but_unvalidated_code(self):
        result = {
            "code": "pass",
            "code_executable": True,
            "code_validation_passed": False,
        }
        with (
            patch("sys.argv", ["run.py", "--file", "examples/problem.txt"]),
            patch("run.get_llm"),
            patch("run.run_trival", return_value=result),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(run.main(), 1)

    def test_missing_api_key_is_reported(self):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("agents.core.llm.load_dotenv"),
        ):
            with self.assertRaisesRegex(RuntimeError, "DEEPSEEK_API_KEY"):
                get_llm()

    def test_deepseek_client_uses_the_official_endpoint(self):
        with (
            patch.dict(
                os.environ, {"DEEPSEEK_API_KEY": "test-placeholder"}, clear=True
            ),
            patch("agents.core.llm.load_dotenv"),
            patch("agents.core.llm.ChatDeepSeek") as client,
        ):
            get_llm("deepseek-flash")
        self.assertEqual(
            client.call_args.kwargs["base_url"], "https://api.deepseek.com"
        )
        self.assertEqual(
            client.call_args.kwargs["extra_body"], {"thinking": {"type": "disabled"}}
        )

    def test_workflow_compiles(self):
        self.assertIsNotNone(create_trival_graph())


if __name__ == "__main__":
    unittest.main()
