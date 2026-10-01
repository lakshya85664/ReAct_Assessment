import pytest

from termination import (
    TerminationError,
    can_continue,
    terminate,
)


def test_completed_termination():
    result = terminate(
        "completed",
        final_answer="Done.",
        current_step=1,
        max_steps=3,
    )

    assert result.terminated is True
    assert result.reason == "completed"


def test_failed_termination():
    result = terminate(
        "failed",
        final_answer="Tool failed.",
        current_step=2,
        max_steps=3,
    )

    assert result.terminated is True
    assert result.reason == "failed"


def test_step_limit_termination():
    result = terminate(
        "step_limit",
        current_step=3,
        max_steps=3,
    )

    assert result.terminated is True
    assert result.reason == "step_limit"


def test_invalid_completed_termination_is_rejected():
    with pytest.raises(
        TerminationError,
        match="requires a final answer",
    ):
        terminate(
            "completed",
            final_answer="",
            current_step=1,
            max_steps=3,
        )


def test_continue_is_false_at_limit():
    assert can_continue(
        current_step=1,
        max_steps=3,
    ) is True

    assert can_continue(
        current_step=3,
        max_steps=3,
    ) is False