from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


class ActionSelectionError(ValueError):
    """Raised when an action cannot be safely selected."""


@dataclass(frozen=True)
class Action:
    """Validated action selected by the ReAct controller."""

    name: str
    args: dict[str, Any]


def select_action(
    action_name: str,
    args: dict[str, Any],
    tools: dict[str, Callable[..., Any]],
) -> Action:
    """
    Validate and select an available tool action.

    The function only selects a registered action. It does not execute it.
    """

    if not isinstance(action_name, str) or not action_name.strip():
        raise ActionSelectionError("action name cannot be empty")

    action_name = action_name.strip()

    if not isinstance(args, dict):
        raise ActionSelectionError("action arguments must be a dictionary")

    if action_name not in tools:
        raise ActionSelectionError(
            f"action is not registered: {action_name}"
        )

    tool = tools[action_name]

    if not callable(tool):
        raise ActionSelectionError(
            f"registered action is not callable: {action_name}"
        )

    return Action(
        name=action_name,
        args=dict(args),
    )


def validate_action_arguments(
    action: Action,
    required_arguments: dict[str, type],
) -> None:
    """Validate required action arguments before execution."""

    for argument_name, expected_type in required_arguments.items():
        if argument_name not in action.args:
            raise ActionSelectionError(
                f"missing required argument: {argument_name}"
            )

        value = action.args[argument_name]

        if not isinstance(value, expected_type):
            raise ActionSelectionError(
                f"invalid type for argument: {argument_name}"
            )