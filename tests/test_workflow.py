import importlib
import unittest
from collections import Counter
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import Mock, patch

from langchain.messages import AIMessage
from langgraph.graph import END

from agents.graph import (
    route_after_code_execution,
    route_after_code_validation,
    route_formulation_validation,
    route_start_formulation_validation,
)
from agents.nodes.code_validation.tools import write_code
from agents.nodes.formulation_validation.formulation_selector import select_formulation
from agents.nodes.formulation_validation.revise_formulation import write_formulation
from agents.nodes.semantic_validation.semantic_fact_extractor import (
    write_semantic_ambiguities,
    write_semantic_facts,
)
from agents.runner import run_trival
from agents.schema import (
    CodeValidationOutput,
    FormulationValidationOutput,
    SemanticValidationOutput,
)


class WorkflowTests(unittest.TestCase):
    def test_formulation_actions_route_to_local_revision_or_four_experts(self):
        for action, expected in [
            ("partial_revise", "revise_formulation"),
            (
                "reformulate",
                [
                    "parameter_index_expert",
                    "constraint_expert",
                    "decision_variable_expert",
                    "objective_expert",
                ],
            ),
        ]:
            with self.subTest(action=action):
                result = FormulationValidationOutput(
                    formulation_validation_feedback="Correct the formulation.",
                    formulation_validation_passed=False,
                    formulation_revision_action=action,
                )
                self.assertEqual(
                    route_formulation_validation(result.model_dump()), expected
                )
        self.assertEqual(
            route_formulation_validation({"formulation_validation_passed": True}), END
        )

    def test_execution_and_validation_route_using_error_attribution(self):
        self.assertEqual(
            route_after_code_execution({"code_executable": False}), "code_agent"
        )
        self.assertEqual(
            route_after_code_execution({"code_executable": True}), "code_validator"
        )
        self.assertEqual(
            route_after_code_validation({"error_attribution": "formulation"}),
            "formulation_validation",
        )
        self.assertEqual(
            route_start_formulation_validation({"error_attribution": "formulation"}),
            "revise_formulation",
        )
        self.assertEqual(
            route_after_code_validation({"code_validation_passed": True}), END
        )

    def test_selection_tools_copy_complete_candidates_to_the_formulation(self):
        for expert, field in [
            ("parameter_index_expert", "parameter_index_candidate"),
            ("decision_variable_expert", "decision_variable_candidate"),
            ("constraint_expert", "constraint_candidate"),
            ("objective_expert", "objective_candidate"),
        ]:
            with self.subTest(expert=expert):
                runtime = SimpleNamespace(
                    state={field: "Complete formulation"}, tool_call_id="selection"
                )
                update = select_formulation.func(
                    expert_name=expert, runtime=runtime
                ).update
                self.assertEqual(update["formulation"], "Complete formulation")
                self.assertEqual(update["selected_formulation_expert"], expert)
                self.assertEqual(update["messages"][0].name, "select_formulation")

    def test_workflow_preserves_feedback_across_all_revision_loops(self):
        calls = Counter()
        experts = {
            "parameter_index_expert",
            "decision_variable_expert",
            "constraint_expert",
            "objective_expert",
        }
        actors = {
            **{name: "formulation_validation" for name in experts},
            "formulation_selector": "formulation_validation",
            "formulation_validator": "formulation_validation",
            "revise_formulation": "formulation_validation",
            "semantic_fact_extractor": "semantic_validation",
            "ambiguity_resolver": "semantic_validation",
            "semantic_validator": "semantic_validation",
            "code_agent": "code_validation",
            "code_validator": "code_validation",
        }

        def fake_create_agent(**kwargs):
            name = kwargs["name"]

            def invoke(state, **invoke_kwargs):
                calls[name] += 1
                attempt = calls[name]
                runtime = SimpleNamespace(state=state, tool_call_id=f"{name}-{attempt}")
                if name == "semantic_fact_extractor":
                    if attempt == 2:
                        self.assertEqual(
                            state["semantic_validation_feedback"], "Correct the facts."
                        )
                    return {
                        **write_semantic_facts.func(
                            semantic_facts="Facts", runtime=runtime
                        ).update,
                        **write_semantic_ambiguities.func(
                            semantic_ambiguities="Ambiguity", runtime=runtime
                        ).update,
                    }
                if name == "ambiguity_resolver":
                    return {"messages": [AIMessage(content="Adopted resolution")]}
                if name == "semantic_validator":
                    return {
                        "structured_response": SemanticValidationOutput(
                            facts_faithful=attempt > 1,
                            ambiguities_relevant=True,
                            resolutions_consistent=True,
                            feedback="Correct the facts." if attempt == 1 else None,
                        )
                    }
                if name in experts:
                    if attempt == 2:
                        self.assertEqual(
                            state["formulation_revision_action"], "reformulate"
                        )
                        self.assertEqual(
                            state["formulation_validation_feedback"],
                            "Correct the formulation.",
                        )
                    return {
                        "messages": [
                            AIMessage(content=f"Complete candidate from {name}")
                        ]
                    }
                if name == "formulation_selector":
                    return select_formulation.func(
                        expert_name="decision_variable_expert", runtime=runtime
                    ).update
                if name == "formulation_validator":
                    action = {1: "reformulate", 2: "partial_revise"}.get(attempt)
                    return {
                        "structured_response": FormulationValidationOutput(
                            formulation_validation_feedback="Correct the formulation.",
                            formulation_validation_passed=action is None,
                            formulation_revision_action=action,
                        )
                    }
                if name == "revise_formulation":
                    if attempt == 2:
                        self.assertEqual(state["error_attribution"], "formulation")
                        self.assertEqual(
                            state["code_validation_feedback"],
                            "Correct the formulation defect.",
                        )
                    return write_formulation.func(
                        formulation="Corrected formulation", runtime=runtime
                    ).update
                if name == "code_agent":
                    if attempt == 2:
                        self.assertFalse(state["code_executable"])
                        self.assertIn("RuntimeError", state["execution_feedback"])
                    if attempt == 3:
                        self.assertEqual(
                            state["code_validation_feedback"],
                            "Correct the code defect.",
                        )
                    code = (
                        "raise RuntimeError('retry')"
                        if attempt == 1
                        else "print('solution')"
                    )
                    return write_code.func(code=code, runtime=runtime).update
                if name == "code_validator":
                    attribution = "formulation" if attempt == 2 else "code"
                    return {
                        "structured_response": CodeValidationOutput(
                            code_validation_passed=attempt == 3,
                            code_validation_feedback=f"Correct the {attribution} defect.",
                            error_attribution=attribution,
                        )
                    }
                raise AssertionError(f"Unexpected actor: {name}")

            return Mock(invoke=invoke)

        with ExitStack() as stack:
            for name, stage in actors.items():
                module = importlib.import_module(f"agents.nodes.{stage}.{name}")
                stack.enter_context(
                    patch.object(module, "create_agent", side_effect=fake_create_agent)
                )
            stack.enter_context(patch("agents.core.logger.logger.disabled", True))
            result = run_trival(
                problem_description="Test problem", context={"llm": Mock()}
            )

        self.assertEqual(result["problem_description"], "Test problem")
        self.assertEqual(result["formulation"], "Corrected formulation")
        self.assertEqual(
            result["selected_formulation_expert"], "decision_variable_expert"
        )
        self.assertEqual(result["ambiguity_resolutions"], "Adopted resolution")
        self.assertTrue(result["code_executable"])
        self.assertTrue(result["code_validation_passed"])
        self.assertEqual(result["execution_feedback"], "solution\n")
        self.assertEqual(result["semantic_validation_count"], 2)
        self.assertEqual(result["formulation_validation_count"], 4)
        self.assertEqual(result["code_validation_count"], 3)
        self.assertEqual(result["code_execution_count"], 4)
        self.assertEqual(calls["ambiguity_resolver"], 1)
        self.assertEqual(calls["revise_formulation"], 2)
        for expert in experts:
            self.assertEqual(calls[expert], 2)


if __name__ == "__main__":
    unittest.main()
