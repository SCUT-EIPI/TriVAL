import importlib
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import httpx
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain.messages import HumanMessage
from langgraph.graph import END

from agents.core.deepseek import ChatDeepSeek
from agents.graph import (
    route_after_code_execution,
    route_after_code_validation,
    route_code_validation,
)
from agents.nodes.code_validation.code_agent import code_agent
from agents.nodes.formulation_validation.formulation_selector import select_formulation
from agents.nodes.semantic_validation.semantic_fact_extractor import (
    semantic_fact_extractor,
    write_semantic_ambiguities,
)
from agents.schema import SemanticValidationOutput
from experiments.manager import NL4COPManager
from experiments.manager._loader import load_jsonl_records


def offline_model(handler):
    return ChatDeepSeek(
        model="deepseek-flash",
        api_key="offline-placeholder",
        base_url="https://api.deepseek.com",
        extra_body={"thinking": {"type": "disabled"}},
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )


def response(message):
    return httpx.Response(
        200,
        json={
            "id": "offline",
            "object": "chat.completion",
            "created": 0,
            "model": "deepseek-flash",
            "choices": [{"index": 0, "message": message, "finish_reason": "stop"}],
        },
    )


def tool_call(name, arguments, call_id):
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.addCleanup(patch.stopall)
        patch("agents.core.logger.logger.disabled", True).start()

    def test_validator_keeps_required_tool_choice(self):
        requests = []

        def handler(request):
            payload = json.loads(request.content)
            requests.append(payload)
            if payload.get("tool_choice") != "required":
                return response({"role": "assistant", "content": "Valid."})
            name = payload["tools"][0]["function"]["name"]
            values = {
                "facts_faithful": True,
                "ambiguities_relevant": True,
                "resolutions_consistent": True,
                "feedback": None,
            }
            return response(
                {
                    "role": "assistant",
                    "content": None,
                    "tool_calls": [tool_call(name, values, "validation")],
                }
            )

        agent = create_agent(
            model=offline_model(handler),
            tools=[],
            response_format=ToolStrategy(SemanticValidationOutput),
        )
        result = agent.invoke(
            {"messages": [HumanMessage(content="Validate.")]},
            config={"recursion_limit": 10},
        )
        self.assertTrue(result["structured_response"].facts_faithful)
        self.assertEqual(len(requests), 1)

    def test_multiple_code_tools_use_the_latest_code(self):
        for calls, expected in [
            (
                [
                    tool_call(
                        "edit_code", {"search": "x = 1", "replace": "x = 2"}, "x"
                    ),
                    tool_call(
                        "edit_code", {"search": "y = 1", "replace": "y = 2"}, "y"
                    ),
                ],
                "x = 2\ny = 2",
            ),
            (
                [
                    tool_call("write_code", {"code": "x = 2"}, "write"),
                    tool_call(
                        "edit_code", {"search": "x = 2", "replace": "x = 3"}, "edit"
                    ),
                ],
                "x = 3",
            ),
        ]:
            with self.subTest(expected=expected):
                requests = []

                def handler(request):
                    payload = json.loads(request.content)
                    requests.append(payload)
                    if len(requests) == 1:
                        return response(
                            {"role": "assistant", "content": None, "tool_calls": calls}
                        )
                    return response({"role": "assistant", "content": "Done."})

                result = code_agent(
                    {
                        "problem_description": "P",
                        "formulation": "M",
                        "code": "x = 1\ny = 1",
                    },
                    {"recursion_limit": 10},
                    SimpleNamespace(context={"llm": offline_model(handler)}),
                )
                self.assertEqual(result["code"], expected)
                replies = [
                    message
                    for message in requests[1]["messages"]
                    if message["role"] == "tool"
                ]
                self.assertEqual(
                    [item["tool_call_id"] for item in replies],
                    [item["id"] for item in calls],
                )

    def test_current_execution_error_is_visible_and_previous_validation_is_invalidated(
        self,
    ):
        module = importlib.import_module("agents.nodes.code_validation.code_agent")
        agent = Mock()
        agent.invoke.return_value = {"code": "pass"}
        state = {
            "problem_description": "P",
            "formulation": "M",
            "code": "pass",
            "code_validation_passed": False,
            "code_validation_feedback": "OLD_VALIDATION",
            "code_executable": False,
            "execution_feedback": "NEW_RUNTIME_ERROR",
        }
        with patch.object(module, "create_agent", return_value=agent):
            result = code_agent(state, {}, SimpleNamespace(context={"llm": Mock()}))
        message = agent.invoke.call_args.args[0]["messages"][0].content
        self.assertIn("NEW_RUNTIME_ERROR", message)
        self.assertIsNone(result["code_validation_passed"])
        self.assertIsNone(result["code_validation_feedback"])

    def test_removed_ambiguity_does_not_survive_without_a_tool_call(self):
        module = importlib.import_module(
            "agents.nodes.semantic_validation.semantic_fact_extractor"
        )
        state = {
            "problem_description": "P",
            "semantic_facts": "Facts",
            "semantic_ambiguities": "Spurious ambiguity",
            "ambiguity_resolutions": "Unsupported convention",
            "resolutions_consistent": True,
            "ambiguities_relevant": False,
            "semantic_validation_feedback": "Remove the ambiguity.",
        }
        agent = Mock(
            invoke=lambda current, **kwargs: {
                **current,
                "semantic_facts": "Corrected facts",
            }
        )
        with patch.object(module, "create_agent", return_value=agent):
            result = semantic_fact_extractor(
                state, {}, SimpleNamespace(context={"llm": Mock()})
            )
        self.assertFalse(result["semantic_ambiguities"])
        self.assertIsNone(result["ambiguity_resolutions"])
        self.assertIsNone(result["resolutions_consistent"])

    def test_changed_ambiguity_invalidates_its_resolution(self):
        state = {
            "semantic_ambiguities": "Old ambiguity",
            "ambiguity_resolutions": "Old resolution",
            "resolutions_consistent": True,
        }
        for value in ["", "Different ambiguity"]:
            with self.subTest(value=value):
                result = write_semantic_ambiguities.func(
                    value, SimpleNamespace(state=state, tool_call_id="update")
                ).update
                self.assertIsNone(result["ambiguity_resolutions"])
                self.assertIsNone(result["resolutions_consistent"])

    def test_execution_budget_boundary_preserves_validation(self):
        self.assertEqual(
            route_after_code_execution(
                {"code_execution_count": 20, "code_executable": True}
            ),
            "code_validator",
        )
        self.assertEqual(
            route_after_code_execution(
                {"code_execution_count": 20, "code_executable": False}
            ),
            END,
        )
        self.assertEqual(
            route_code_validation(
                {
                    "code_execution_count": 20,
                    "code_validation_passed": False,
                    "error_attribution": "code",
                }
            ),
            END,
        )
        self.assertEqual(
            route_after_code_validation(
                {
                    "code_execution_count": 20,
                    "code_validation_passed": False,
                    "error_attribution": "formulation",
                }
            ),
            END,
        )

    def test_unknown_expert_returns_tool_feedback(self):
        result = select_formulation.func(
            "unknown", SimpleNamespace(state={}, tool_call_id="selection")
        )
        self.assertNotIn("formulation", result.update)
        self.assertIn("Error:", result.update["messages"][0].content)

    def test_nl4cop_rejects_corrupt_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "a.json").write_text("{broken json")
            (path / "b.json").write_text(
                json.dumps({"problem_id": "b", "problem_description": "Problem B"})
            )
            with self.assertRaises(json.JSONDecodeError):
                NL4COPManager(directory)

    def test_jsonl_loader_preserves_order_and_reports_invalid_records(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.jsonl"
            records = [{"id": "b", "question": "B"}, {"id": "a", "question": "A"}]
            path.write_text("\n" + "\n\n".join(json.dumps(item) for item in records))
            self.assertEqual(load_jsonl_records(path, ("id", "question")), records)
            for content, error in [
                ("", ValueError),
                ("[]", ValueError),
                ("{}", KeyError),
                ("{broken", json.JSONDecodeError),
            ]:
                with self.subTest(content=content):
                    path.write_text(content)
                    with self.assertRaises(error):
                        load_jsonl_records(path, ("id", "question"))

    def test_formulation_revision_invalidates_code_feedback(self):
        module = importlib.import_module(
            "agents.nodes.formulation_validation.revise_formulation"
        )
        agent = Mock()
        agent.invoke.return_value = {"formulation": "Corrected formulation"}
        state = {
            "problem_description": "P",
            "formulation": "M",
            "code_validation_passed": False,
            "code_validation_feedback": "FORMULATION_DEFECT",
            "error_attribution": "formulation",
            "code_executable": True,
            "execution_feedback": "Old output",
        }
        with patch.object(module, "create_agent", return_value=agent):
            result = module.revise_formulation(
                state, {}, SimpleNamespace(context={"llm": Mock()})
            )
        self.assertIn(
            "FORMULATION_DEFECT", agent.invoke.call_args.args[0]["messages"][0].content
        )
        for field in [
            "error_attribution",
            "code_validation_passed",
            "code_validation_feedback",
            "code_executable",
            "execution_feedback",
        ]:
            self.assertIsNone(result[field])


if __name__ == "__main__":
    unittest.main()
