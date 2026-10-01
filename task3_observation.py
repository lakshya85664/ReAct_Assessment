import json
from pathlib import Path

from observation import (
    ObservationError,
    create_observation,
    tool_result_to_observation,
)


TRACE_PATH = Path("traces/task3_observation.jsonl")


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def main() -> None:
    TRACE_PATH.unlink(missing_ok=True)

    print("=" * 65)
    print("Topic 10 — Task 3: Observation")
    print("=" * 65)

    # ------------------------------------------------------------
    # CASE 1 — SUCCESSFUL TOOL OBSERVATION
    # ------------------------------------------------------------
    observation = tool_result_to_observation(
        tool_name="lookup",
        result="order:88213 status:verified",
    )

    print("\nCASE 1 — SUCCESSFUL OBSERVATION")
    print(f"source: {observation.source}")
    print(f"content: {observation.content}")
    print(f"success: {observation.success}")

    write_trace(
        {
            "case": "successful_observation",
            "status": "passed",
            "result": "accepted",
            "source": observation.source,
            "content": observation.content,
            "success": observation.success,
        }
    )

    # ------------------------------------------------------------
    # CASE 2 — TOOL FAILURE BECOMES OBSERVATION
    # ------------------------------------------------------------
    failure = tool_result_to_observation(
        tool_name="lookup",
        error="temporary service unavailable",
    )

    print("\nCASE 2 — TOOL FAILURE AS OBSERVATION")
    print(f"source: {failure.source}")
    print(f"content: {failure.content}")
    print(f"success: {failure.success}")

    write_trace(
        {
            "case": "tool_failure_observation",
            "status": "passed",
            "result": "converted_to_observation",
            "source": failure.source,
            "content": failure.content,
            "success": failure.success,
        }
    )

    # ------------------------------------------------------------
    # CASE 3 — EXPLICIT OBSERVATION
    # ------------------------------------------------------------
    observation = create_observation(
        source="environment",
        content="customer requested human review",
        success=True,
    )

    print("\nCASE 3 — EXPLICIT OBSERVATION")
    print(f"source: {observation.source}")
    print(f"content: {observation.content}")
    print(f"success: {observation.success}")

    write_trace(
        {
            "case": "explicit_observation",
            "status": "passed",
            "result": "accepted",
            "source": observation.source,
            "content": observation.content,
            "success": observation.success,
        }
    )

    # ------------------------------------------------------------
    # CASE 4 — EMPTY CONTENT REJECTED
    # ------------------------------------------------------------
    try:
        create_observation(
            source="lookup",
            content="",
            success=True,
        )
    except ObservationError as exc:
        print("\nCASE 4 — EMPTY OBSERVATION REJECTED")
        print("status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "empty_observation",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    # ------------------------------------------------------------
    # CASE 5 — BOTH RESULT AND ERROR REJECTED
    # ------------------------------------------------------------
    try:
        tool_result_to_observation(
            tool_name="lookup",
            result="some result",
            error="some error",
        )
    except ObservationError as exc:
        print("\nCASE 5 — CONFLICTING TOOL RESULT REJECTED")
        print("status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "conflicting_tool_result",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    print("\nTRACE")
    print(TRACE_PATH)

    print("\nTask 3 demonstration complete.")


if __name__ == "__main__":
    main()