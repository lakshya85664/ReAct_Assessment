import pytest

from react import ReActState, ReActStateError


def test_valid_initial_state():
    state = ReActState(
        question="Find order 88213",
        tools={"lookup": "lookup tool"},
        max_steps=3,
    )

    assert state.question == "Find order 88213"
    assert state.tools["lookup"] == "lookup tool"
    assert state.step == 0
    assert state.max_steps == 3
    assert state.observations == []
    assert state.status == "running"


def test_observation_and_step_advance():
    state = ReActState(
        question="Find order 88213",
        tools={"lookup": "lookup tool"},
    )

    state.add_observation("order:88213 status:verified")
    step = state.advance()

    assert step == 1
    assert state.step == 1
    assert state.observations == ["order:88213 status:verified"]


def test_completion_stores_final_answer():
    state = ReActState(
        question="Find order 88213",
        tools={"lookup": "lookup tool"},
    )

    state.complete("Order 88213 is verified.")

    assert state.status == "completed"
    assert state.final_answer == "Order 88213 is verified."


def test_empty_question_is_rejected():
    with pytest.raises(ReActStateError, match="question cannot be empty"):
        ReActState(
            question="   ",
            tools={"lookup": "lookup tool"},
        )


def test_step_limit_is_enforced():
    state = ReActState(
        question="Bounded loop test",
        tools={"lookup": "lookup tool"},
        max_steps=1,
    )

    state.advance()

    with pytest.raises(ReActStateError, match="step limit reached"):
        state.advance()

    assert state.step == 1
    assert state.status == "stopped"