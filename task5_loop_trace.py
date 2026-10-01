import json
from pathlib import Path

from react_loop import run_react_loop


TRACE_PATH = Path("traces/task5_loop_trace.jsonl")


def lookup_order(query: str) -> str:
    if query == "order 88213":
        return "order:88213 status:verified"

    return f"order not found: {query}"


def failing_lookup(query: str) -> str:
    raise RuntimeError("temporary service unavailable")


TOOLS = {
    "lookup": lookup_order,
    "failing_lookup": failing_lookup,
}


def save_trace(name: str, result) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(
            json.dumps(
                {
                    "case": name,
                    "status": result.status,
                    "final_answer": result.final_answer,
                    "steps": result.steps,
                    "observations": result.observations,
                    "trace": result.trace,
                }
            )
            + "\n"
        )


def main() -> None:
    TRACE_PATH.unlink(missing_ok=True)

    print("=" * 65)
    print("Topic 10 — Task 5: ReAct Loop Trace")
    print("=" * 65)

    # ------------------------------------------------------------
    # CASE 1 — SUCCESSFUL MULTI-STEP LOOP
    # ------------------------------------------------------------
    result = run_react_loop(
        question="What is the status of order 88213?",
        tools=TOOLS,
        plan=[
            {
                "action": "lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
                "final_answer": "Order 88213 is verified.",
            }
        ],
        max_steps=3,
    )

    print("\nCASE 1 — SUCCESSFUL LOOP")
    print(f"status: {result.status}")
    print(f"steps: {result.steps}")
    print(f"final_answer: {result.final_answer}")

    save_trace("successful_loop", result)

    # ------------------------------------------------------------
    # CASE 2 — TOOL FAILURE AS OBSERVATION
    # ------------------------------------------------------------
    result = run_react_loop(
        question="Recover from a temporary lookup failure",
        tools=TOOLS,
        plan=[
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
                "final_answer": "Order 88213 is verified after recovery.",
            },
        ],
        max_steps=3,
    )

    print("\nCASE 2 — FAILURE THEN RECOVERY")
    print(f"status: {result.status}")
    print(f"steps: {result.steps}")
    print(f"observations: {len(result.observations)}")
    print(f"final_answer: {result.final_answer}")

    save_trace("failure_then_recovery", result)

    # ------------------------------------------------------------
    # CASE 3 — STEP LIMIT
    # ------------------------------------------------------------
    result = run_react_loop(
        question="Demonstrate bounded execution",
        tools=TOOLS,
        plan=[
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
        ],
        max_steps=2,
    )

    print("\nCASE 3 — STEP LIMIT")
    print(f"status: {result.status}")
    print(f"steps: {result.steps}")
    print(f"final_answer: {result.final_answer}")

    save_trace("step_limit", result)

    print("\nTRACE")
    print(TRACE_PATH)

    print("\nTask 5 demonstration complete.")


if __name__ == "__main__":
    main()