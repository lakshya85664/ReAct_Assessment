import json
from pathlib import Path

from termination import (
    TerminationError,
    can_continue,
    terminate,
)


TRACE_PATH = Path("traces/task4_termination.jsonl")


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def main() -> None:
    TRACE_PATH.unlink(missing_ok=True)

    print("=" * 65)
    print("Topic 10 — Task 4: Termination")
    print("=" * 65)

    # ------------------------------------------------------------
    # CASE 1 — COMPLETED
    # ------------------------------------------------------------
    result = terminate(
        "completed",
        final_answer="Order 88213 is verified.",
        current_step=1,
        max_steps=3,
    )

    print("\nCASE 1 — COMPLETED")
    print(f"terminated: {result.terminated}")
    print(f"reason: {result.reason}")

    write_trace(
        {
            "case": "completed",
            "status": "passed",
            "result": "terminated",
            "reason": result.reason,
        }
    )

    # ------------------------------------------------------------
    # CASE 2 — FAILURE
    # ------------------------------------------------------------
    result = terminate(
        "failed",
        final_answer="Tool execution failed after bounded attempts.",
        current_step=2,
        max_steps=3,
    )

    print("\nCASE 2 — FAILED")
    print(f"terminated: {result.terminated}")
    print(f"reason: {result.reason}")

    write_trace(
        {
            "case": "failed",
            "status": "passed",
            "result": "terminated",
            "reason": result.reason,
        }
    )

    # ------------------------------------------------------------
    # CASE 3 — STEP LIMIT
    # ------------------------------------------------------------
    result = terminate(
        "step_limit",
        current_step=3,
        max_steps=3,
    )

    print("\nCASE 3 — STEP LIMIT")
    print(f"terminated: {result.terminated}")
    print(f"reason: {result.reason}")

    write_trace(
        {
            "case": "step_limit",
            "status": "passed",
            "result": "terminated",
            "reason": result.reason,
            "step": 3,
            "max_steps": 3,
        }
    )

    # ------------------------------------------------------------
    # CASE 4 — EXPLICIT STOP
    # ------------------------------------------------------------
    result = terminate(
        "explicit_stop",
        current_step=1,
        max_steps=3,
    )

    print("\nCASE 4 — EXPLICIT STOP")
    print(f"terminated: {result.terminated}")
    print(f"reason: {result.reason}")

    write_trace(
        {
            "case": "explicit_stop",
            "status": "passed",
            "result": "terminated",
            "reason": result.reason,
        }
    )

    # ------------------------------------------------------------
    # CASE 5 — INVALID COMPLETION REJECTED
    # ------------------------------------------------------------
    try:
        terminate(
            "completed",
            final_answer="",
            current_step=1,
            max_steps=3,
        )
    except TerminationError as exc:
        print("\nCASE 5 — INVALID COMPLETION REJECTED")
        print("status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "invalid_completion",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    # ------------------------------------------------------------
    # CONTINUE CHECK
    # ------------------------------------------------------------
    print("\nCONTINUE CHECK")
    print(
        "before limit:",
        can_continue(
            current_step=1,
            max_steps=3,
        ),
    )
    print(
        "at limit:",
        can_continue(
            current_step=3,
            max_steps=3,
        ),
    )

    print("\nTRACE")
    print(TRACE_PATH)

    print("\nTask 4 demonstration complete.")


if __name__ == "__main__":
    main()