import json
from pathlib import Path

from action_selection import (
    ActionSelectionError,
    select_action,
    validate_action_arguments,
)


TRACE_PATH = Path("traces/task2_action_selection.jsonl")


def lookup_order(query: str) -> str:
    return f"lookup result for: {query}"


TOOLS = {
    "lookup": lookup_order,
}


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def main() -> None:
    TRACE_PATH.unlink(missing_ok=True)

    print("=" * 65)
    print("Topic 10 — Task 2: Action Selection")
    print("=" * 65)

    # ------------------------------------------------------------
    # CASE 1 — VALID ACTION SELECTION
    # ------------------------------------------------------------
    action = select_action(
        action_name="lookup",
        args={"query": "order 88213"},
        tools=TOOLS,
    )

    validate_action_arguments(
        action,
        {"query": str},
    )

    print("\nCASE 1 — VALID ACTION")
    print(f"action: {action.name}")
    print(f"args: {action.args}")

    write_trace(
        {
            "case": "valid_action",
            "status": "passed",
            "result": "selected",
            "action": action.name,
            "args": action.args,
        }
    )

    # ------------------------------------------------------------
    # CASE 2 — VALIDATION BEFORE EXECUTION
    # ------------------------------------------------------------
    action = select_action(
        action_name="lookup",
        args={"query": "order 99111"},
        tools=TOOLS,
    )

    validate_action_arguments(
        action,
        {"query": str},
    )

    print("\nCASE 2 — VALIDATED ARGUMENTS")
    print(f"action: {action.name}")
    print("argument validation: passed")

    write_trace(
        {
            "case": "argument_validation",
            "status": "passed",
            "result": "validated",
            "action": action.name,
        }
    )

    # ------------------------------------------------------------
    # CASE 3 — UNKNOWN ACTION REJECTED
    # ------------------------------------------------------------
    try:
        select_action(
            action_name="delete_order",
            args={"order_id": "88213"},
            tools=TOOLS,
        )
    except ActionSelectionError as exc:
        print("\nCASE 3 — UNKNOWN ACTION REJECTED")
        print("status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "unknown_action",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    # ------------------------------------------------------------
    # CASE 4 — MISSING REQUIRED ARGUMENT
    # ------------------------------------------------------------
    try:
        action = select_action(
            action_name="lookup",
            args={},
            tools=TOOLS,
        )

        validate_action_arguments(
            action,
            {"query": str},
        )
    except ActionSelectionError as exc:
        print("\nCASE 4 — INVALID ARGUMENTS REJECTED")
        print("status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "invalid_arguments",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    # ------------------------------------------------------------
    # CASE 5 — WRONG ARGUMENT TYPE
    # ------------------------------------------------------------
    try:
        action = select_action(
            action_name="lookup",
            args={"query": 88213},
            tools=TOOLS,
        )

        validate_action_arguments(
            action,
            {"query": str},
        )
    except ActionSelectionError as exc:
        print("\nCASE 5 — WRONG ARGUMENT TYPE REJECTED")
        print("status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "wrong_argument_type",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    print("\nTRACE")
    print(TRACE_PATH)

    print("\nTask 2 demonstration complete.")


if __name__ == "__main__":
    main()