import json
from pathlib import Path

from react import ReActState, ReActStateError


TRACE_PATH = Path("traces/task1_react_state.jsonl")


def write_trace(record: dict) -> None:
    TRACE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with TRACE_PATH.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")


def main() -> None:
    TRACE_PATH.unlink(missing_ok=True)

    print("=" * 65)
    print("Topic 10 — Task 1: ReAct State")
    print("=" * 65)

    # ------------------------------------------------------------
    # CASE 1 — VALID INITIAL STATE
    # ------------------------------------------------------------
    state = ReActState(
        question="What is the status of order 88213?",
        tools={"lookup": "order lookup tool"},
        max_steps=3,
    )

    print("\nCASE 1 — VALID INITIAL STATE")
    print(json.dumps(state.snapshot(), indent=2))

    write_trace(
        {
            "case": "valid_initial_state",
            "status": "passed",
            "result": "accepted",
            "detail": "valid ReAct state created",
            "snapshot": state.snapshot(),
        }
    )

    # ------------------------------------------------------------
    # CASE 2 — OBSERVATION
    # ------------------------------------------------------------
    state.add_observation("order:88213 status:verified")
    current_step = state.advance()

    print("\nCASE 2 — OBSERVATION + STEP ADVANCE")
    print(f"observation: {state.observations[-1]}")
    print(f"current_step: {current_step}")

    write_trace(
        {
            "case": "observation_and_step",
            "status": "passed",
            "result": "accepted",
            "detail": "observation recorded and state advanced",
            "snapshot": state.snapshot(),
        }
    )

    # ------------------------------------------------------------
    # CASE 3 — COMPLETION
    # ------------------------------------------------------------
    state.complete("Order 88213 is verified.")

    print("\nCASE 3 — COMPLETION")
    print(json.dumps(state.snapshot(), indent=2))

    write_trace(
        {
            "case": "completion",
            "status": "passed",
            "result": "completed",
            "detail": "final answer stored in ReAct state",
            "snapshot": state.snapshot(),
        }
    )

    # ------------------------------------------------------------
    # CASE 4 — INVALID QUESTION
    # ------------------------------------------------------------
    try:
        ReActState(
            question="",
            tools={"lookup": "order lookup tool"},
        )
    except ReActStateError as exc:
        print("\nCASE 4 — EMPTY QUESTION REJECTED")
        print(f"status: rejected")
        print(f"reason: {exc}")

        write_trace(
            {
                "case": "empty_question",
                "status": "passed",
                "result": "rejected",
                "detail": str(exc),
            }
        )

    # ------------------------------------------------------------
    # CASE 5 — STEP LIMIT
    # ------------------------------------------------------------
    limited = ReActState(
        question="Test bounded ReAct loop",
        tools={"lookup": "lookup tool"},
        max_steps=1,
    )

    limited.advance()

    try:
        limited.advance()
    except ReActStateError as exc:
        print("\nCASE 5 — STEP LIMIT ENFORCED")
        print(f"status: rejected")
        print(f"reason: {exc}")
        print(f"state_status: {limited.status}")
        print(f"step: {limited.step}")
        print(f"max_steps: {limited.max_steps}")

        write_trace(
            {
                "case": "step_limit",
                "status": "passed",
                "result": "blocked",
                "detail": str(exc),
                "step": limited.step,
                "max_steps": limited.max_steps,
                "state_status": limited.status,
            }
        )

    print("\nTRACE")
    print(TRACE_PATH)

    print("\nTask 1 demonstration complete.")


if __name__ == "__main__":
    main()  