import pytest

from action_selection import (
    ActionSelectionError,
    select_action,
    validate_action_arguments,
)


def lookup_order(query: str) -> str:
    return f"result: {query}"


TOOLS = {
    "lookup": lookup_order,
}


def test_valid_action_is_selected():
    action = select_action(
        "lookup",
        {"query": "order 88213"},
        TOOLS,
    )

    assert action.name == "lookup"
    assert action.args == {"query": "order 88213"}


def test_valid_arguments_are_accepted():
    action = select_action(
        "lookup",
        {"query": "order 88213"},
        TOOLS,
    )

    validate_action_arguments(
        action,
        {"query": str},
    )


def test_unknown_action_is_rejected():
    with pytest.raises(
        ActionSelectionError,
        match="action is not registered",
    ):
        select_action(
            "delete_order",
            {"order_id": "88213"},
            TOOLS,
        )


def test_missing_argument_is_rejected():
    action = select_action(
        "lookup",
        {},
        TOOLS,
    )

    with pytest.raises(
        ActionSelectionError,
        match="missing required argument",
    ):
        validate_action_arguments(
            action,
            {"query": str},
        )


def test_wrong_argument_type_is_rejected():
    action = select_action(
        "lookup",
        {"query": 88213},
        TOOLS,
    )

    with pytest.raises(
        ActionSelectionError,
        match="invalid type",
    ):
        validate_action_arguments(
            action,
            {"query": str},
        )