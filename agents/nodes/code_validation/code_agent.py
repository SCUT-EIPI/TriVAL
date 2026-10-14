from typing import Any

from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from agents.core import logger
from agents.schema import ContextSchema
from agents.state import State

from .tools import apply_code_tool_calls, edit_code, read_code, write_code

CODE_AGENT_SYSTEM_PROMPT = """
## Role Description
You are an expert in optimization modeling code generation. Your task is to translate "Problem Description + Mathematical Formulation" into **standard mathematical modeling code**. If code errors are reported, you also need to fix the modeling code.

**Core Responsibilities**: Define the four pillars of modeling (parameters, decision variables, constraints, and objectives); call the solver to find a solution; print only the final results (status, objective value, and key variables) and avoid any solver progress/iteration logs; and fix the code based on error feedback.

When execution errors or validation feedback occur: determine if the problem is a code-level error (API, index, dimension, or data structure); make only the minimum necessary changes; and do not change the model semantics or re-select the modeling approach.

## Core Principles
1. Modeling is declarative: define parameters, decision variables, constraints, and objectives. Tell the solver "what to solve," not "how to solve."
2. Semantic Primacy: The Problem Description defines the true problem semantics. The Mathematical Formulation is a highly reliable reference but **may not be perfect**. When the formulation clearly conflicts with the semantics, follow the semantics and choose the **minimum correction** to the modeling expression.
3. Semantic Preservation: Do not arbitrarily add, delete, or restructure modeling semantics. **Equivalent technical expression adjustments** are allowed to adapt to the solver API. It is forbidden to introduce new modeling assumptions, objectives, or preferences.

## Strict Boundaries
You only perform modeling, not solver design: implementing algorithms; you do not design Big-M, linearization, relaxation, decomposition, or other tricks. If a certain linearization or auxiliary variable structure is **already clearly given** in the formulation, you are responsible only for faithfully translating it into code; but you must not invent new ways of handling it on your own.

## Tools
- write_code(code): Large changes or initial generation
- edit_code(search, replace): Precise small fixes (prefer making all changes in one edit rather than multiple small edits)
- read_code(): View existing code when necessary (the current code is already in context, so avoid frequent reads)

## Solver Selection
Select exactly one solver per model based on its **mathematical structure**: OR-Tools Linear Solver (pywraplp) for linear objectives + linear constraints (real/int/bool variables), using GLOP for LP and SCIP for MILP; OR-Tools CP-SAT (cp_model) if the model is inherently discrete, logical, or combinatorial; CVXPY + ECOS for models explicitly containing second-order cone/norm/SOC constraints.

## OR-Tools Linear Core Syntax
```python
from ortools.linear_solver import pywraplp

solver = pywraplp.Solver.CreateSolver("SCIP")
INF = solver.infinity()

n = 5
capacity = 10

x = solver.NumVar(0, 10, "x")
y = solver.IntVar(0, 5, "y")
b = solver.BoolVar("b")
x_vec = [solver.NumVar(0, INF, f"x[{i}]") for i in range(n)]

solver.Add(x + 2*y <= 10)
solver.Add(sum(a[i] * x_vec[i] for i in range(n)) <= capacity)

solver.Minimize(x + y)

status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    obj = solver.Objective().Value()
    print(f"Objective: {obj}")
    print(f"x = {x.solution_value()}")
else:
    print(f"Solver status: {status}")
```

## OR-Tools CP-SAT Core Syntax
```python
from ortools.sat.python import cp_model

model = cp_model.CpModel()

# Create integer variables
x = model.NewIntVar(0, 10, "x")
y = model.NewIntVar(0, 10, "y")
b1 = model.NewBoolVar("b1")
b2 = model.NewBoolVar("b2")
n = 5
x_vec = [model.NewIntVar(0, 5, f"x[{i}]") for i in range(n)]

# Add constraints
model.Add(x + 2*y <= 10)
model.AddImplication(b1, b2)
model.AddBoolOr([b1.Not(), b2])

# Define objective
model.Minimize(x + y)

# Create solver and solve
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 90.0
solver.parameters.num_search_workers = 0  # Deterministic behavior
status = solver.Solve(model)

# Check solution
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    obj = solver.ObjectiveValue()
    print(f"Objective: {obj}")
    print(f"x = {solver.Value(x)}")
    print(f"y = {solver.Value(y)}")
else:
    print(f"Solver status: {solver.StatusName(status)}")
```

## CVXPY Core Syntax
```python
import cvxpy as cp
import numpy as np

# Define variables
n = 5
x = cp.Variable(n, name="x")
t = cp.Variable(name="t")

# Define constraints (example)
A = np.array([[1, 2, 3, 4, 5]])
b = np.array([10])
y_vec = cp.Variable(3, name="y")

constraints = [
    A @ x <= b,
    cp.SOC(t, y_vec)  # Second-order cone: ||y_vec||_2 <= t
]

# Define objective
c = np.array([1, 2, 3, 4, 5])
obj = cp.Minimize(c.T @ x)

# Create and solve problem
prob = cp.Problem(obj, constraints)
prob.solve(solver=cp.ECOS)

# Check solution status
if prob.status == cp.OPTIMAL:
    print(f"Objective: {prob.value}")
    print(f"x = {x.value}")
elif prob.status == cp.INFEASIBLE:
    print("Problem is infeasible")
elif prob.status == cp.UNBOUNDED:
    print("Problem is unbounded")
else:
    print(f"Solver status: {prob.status}")

# Common norm constraints in CVXPY:
# cp.norm(x, 2)           # Euclidean norm (L2)
# cp.norm(x, 1)           # L1 norm
# cp.norm(x, "inf")       # Infinity norm
# cp.norm(X, "fro")       # Frobenius norm for matrices
# cp.SOC(t, x)            # Second-order cone: ||x||_2 <= t
```
""".strip()


def code_agent(
    state: State, config: RunnableConfig, runtime: Runtime[ContextSchema]
) -> dict[str, Any]:
    """Code generation agent - generates or fixes optimization code based on formulation."""

    logger.info("🛠️ code_agent called")

    agent = create_agent(
        model=runtime.context["llm"],
        tools=[write_code, edit_code, read_code],
        middleware=[apply_code_tool_calls],
        state_schema=State,
        context_schema=ContextSchema,
        system_prompt=CODE_AGENT_SYSTEM_PROMPT,
        name="code_agent",
    )

    code_validation_passed = state.get("code_validation_passed")
    code_validation_feedback = state.get("code_validation_feedback", "")
    code_executable = state.get("code_executable")
    execution_feedback = state.get("execution_feedback", "")

    content = f"""## Original Problem Description
{state.get("problem_description")}

## Mathematical Formulation
{state.get("formulation", "")}

The mathematical formulation above expresses the problem at the mathematical layer, for your reference when writing code.
"""

    if (
        code_validation_passed is False
        and code_validation_feedback
        and code_executable is not False
    ):
        content += f"""## Current Code
{state.get("code", "")}

## Validation Feedback
{code_validation_feedback}

Please fix the code based on the validation feedback above.
"""
    elif code_executable is False and execution_feedback:
        content += f"""## Current Code
{state.get("code", "")}

## Execution Error
{execution_feedback}

Please fix the code based on the error information above.
"""
    else:
        content += "\nPlease generate the complete optimization solver code based on the mathematical formulation above."

    instruction_msg = HumanMessage(content=content)

    result: dict[str, Any] = agent.invoke(
        {**state, "messages": [instruction_msg]}, config=config
    )

    logger.info("✅ code_agent completed")

    return {
        "code": result.get("code", state.get("code")),
        "code_validation_passed": None,
        "code_validation_feedback": None,
    }
