# TriVAL terminology

Terms follow the main text of *TriVAL: A Tri-Validation Framework for Faithful Automatic Optimization Modeling*.

## Modeling artifacts

**Problem description (d)**:
The natural-language optimization problem that defines the intended decisions, requirements, and optimization goal.

**Semantic specification (S)**:
The triple of semantic facts (F), formulation-relevant ambiguities (A), and adopted ambiguity resolutions (R).
_Avoid_: Semantic model.

**Mathematical formulation (M)**:
The complete mathematical representation of the problem, comprising parameters (P), decision variables (V), constraints, and objective (O). Use **formulation** as the short name.
_Avoid_: BlueModel, blueprint, consensus model.

**Generated code (C)**:
Solver code that implements the mathematical formulation and reports the solver result.

## Validation stages

**Semantic Validation**:
The stage that constructs and validates the semantic specification for factual faithfulness, ambiguity relevance, and resolution consistency, with revision when needed.

**Formulation Validation**:
The stage that constructs formulation candidates, selects one, and validates its variable-design quality, constraint soundness, and objective alignment, with revision when needed.

**Code Validation**:
The stage that generates solver code, corrects execution errors, and validates implementation fidelity using execution feedback, with revision when needed.

## Construction and validation roles

**Semantic fact extractor**:
The role that extracts semantic facts and identifies formulation-relevant ambiguities from the problem description.
_Avoid_: SM generator.

**Ambiguity resolver**:
The role that determines an adopted interpretation for each identified ambiguity.

**Parameter-and-index expert**:
A formulation expert whose perspective emphasizes known quantities and their index structure.
_Avoid_: Structure-and-parameter expert.

**Decision-variable expert**:
A formulation expert whose perspective emphasizes the representation of core decisions.
_Avoid_: Variable-and-representation expert.

**Constraint expert**:
A formulation expert whose perspective emphasizes the organization and scope of requirements.
_Avoid_: Constraint-and-pattern expert.

**Objective expert**:
A formulation expert whose perspective emphasizes the expression of the optimization goal.
_Avoid_: Objective-and-cost expert.

**Formulation candidate**:
A complete formulation produced by one expert. Each expert produces all four formulation components.

**Formulation selector**:
The LLM-based role that chooses one complete formulation candidate for validation.
_Avoid_: Chief modeling judge, consensus aggregator.

**Semantic validator / formulation validator / code validator**:
The roles that assess the corresponding artifact against its validation criteria and provide feedback for revision.
_Avoid_: Reviewer, auditor.

**Code agent**:
The ReAct-based role that generates and revises solver code through reading, writing, and partial editing tools.

## Revision and execution

**Partial revision (partial_revise)**:
A local formulation correction for an expression-level defect while keeping the overall formulation choice.
_Avoid_: Fix as the formulation revision action.

**Reformulation (reformulate)**:
Renewed multi-expert exploration for a modeling-level defect that requires a different formulation choice.
_Avoid_: Explore as the formulation revision action.

**Code self-correction**:
Revision of code using execution feedback to correct runtime and solver-interface errors.

**Execution feedback**:
The observed output or error information from running the generated code.

**Error attribution**:
The code validator's determination that a detected defect originates in the code or the formulation.
