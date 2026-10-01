import pytest

from observation import (
    ObservationError,
    create_observation,
    tool_result_to_observation,
)


def test_successful_tool_result_becomes_observation():
    observation = tool_result_to_observation(
        tool_name="lookup",
        result="order:88213 status:verified",
    )

    assert observation.source == "lookup"
    assert observation.content == "order:88213 status:verified"
    assert observation.success is True


def test_tool_failure_becomes_failure_observation():
    observation = tool_result_to_observation(
        tool_name="lookup",
        error="temporary service unavailable",
    )

    assert observation.source == "lookup"
    assert observation.content == (
        "tool_error: temporary service unavailable"
    )
    assert observation.success is False


def test_explicit_observation_is_created():
    observation = create_observation(
        source="environment",
        content="review required",
        success=True,
    )

    assert observation.source == "environment"
    assert observation.content == "review required"
    assert observation.success is True


def test_empty_observation_is_rejected():
    with pytest.raises(
        ObservationError,
        match="observation content cannot be empty",
    ):
        create_observation(
            source="lookup",
            content="",
        )


def test_result_and_error_cannot_both_exist():
    with pytest.raises(
        ObservationError,
        match="result and error cannot both be provided",
    ):
        tool_result_to_observation(
            tool_name="lookup",
            result="result",
            error="error",
        )