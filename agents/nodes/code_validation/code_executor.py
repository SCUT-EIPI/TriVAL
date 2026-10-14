import subprocess
import sys

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime

from agents.core import logger
from agents.schema import ContextSchema
from agents.state import State


def execute_code(code: str, timeout: int = 100) -> tuple[bool, str]:
    """Run code in the current Python interpreter and capture output. The 100s default includes a 10s buffer over the solver budget."""
    if not isinstance(code, str):
        code = str(code)

    env_setup = """\
import warnings

warnings.filterwarnings('ignore')
"""
    code = env_setup + code

    cmd = [sys.executable, "-"]

    try:
        proc = subprocess.run(
            cmd,
            input=code,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        output_chunks = []
        if exc.stdout:
            output_chunks.append(_coerce_to_text(exc.stdout))
        if exc.stderr:
            output_chunks.append(_coerce_to_text(exc.stderr))
        output_chunks.append(
            f"[Code Executor] Code execution timed out (> {timeout} seconds)."
        )
        return False, "\n".join(output_chunks)

    success = proc.returncode == 0
    if success:
        output = proc.stdout or ""
    else:
        output_parts = []
        if proc.stdout:
            output_parts.append(proc.stdout)
        if proc.stderr:
            output_parts.append(proc.stderr)
        output = "\n".join(part for part in output_parts if part)

    return success, output


def code_executor(
    state: State, config: RunnableConfig, runtime: Runtime[ContextSchema]
):
    """Execute Python code in state.code and backfill the execution results."""
    code = state.get("code") or ""
    execution_count = state.get("code_execution_count", 0)

    if not code:
        logger.warning("⚠️ code_executor: state.code is empty")
        return {
            "code_executable": False,
            "execution_feedback": "[Code Executor] state.code is empty, no code executed.",
            "code_execution_count": execution_count + 1,
        }

    logger.info("🚀 code_executor: Executing code (attempt %d)", execution_count + 1)

    success, output = execute_code(code, timeout=100)

    if success:
        logger.info(
            "✅ code_executor: Execution succeeded\n%s", _format_output_block(output)
        )
    else:
        logger.error(
            "❌ code_executor: Execution failed\n%s", _format_output_block(output)
        )

    return {
        "code_executable": success,
        "execution_feedback": output,
        "code_execution_count": execution_count + 1,
    }


def _format_output_block(output: str, max_lines: int = 30) -> str:
    """Format output content, adding borders for readability."""
    if not output:
        return "    (no output)"

    lines = output.strip().split("\n")
    if len(lines) > max_lines:
        lines = lines[:max_lines] + [f"... ({len(lines) - max_lines} lines omitted)"]

    border = "    " + "─" * 60
    indented = "\n".join("    │ " + line for line in lines)
    return f"{border}\n{indented}\n{border}"


def _coerce_to_text(value) -> str:
    """Best-effort decode for subprocess outputs that may be bytes."""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)
