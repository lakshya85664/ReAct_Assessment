from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from action_selection import (
    ActionSelectionError,
    select_action,
    validate_action_arguments,
)
from observation import (
    Observation,
    tool_result_to_observation,
)
from termination import (
    TerminationError,
    can_continue,
    terminate,
)


class ReActLoopError(RuntimeError):
    """Raised when the ReAct loop cannot continue safely."""


@dataclass
class LoopResult:
    status: str
    final_answer: str | None
    steps: int
    observations: list[dict[str, Any]]
    trace: list[dict[str, Any]]


def run_react_loop(
    question: str,
    tools: dict[str, Callable[..., str]],
    plan: list[dict[str, Any]],
    *,
    max_steps: int = 5,
) -> LoopResult:
    """
    Execute a bounded deterministic ReAct loop.

    Each plan entry contains:
      action: registered tool name
      args: tool arguments

    The loop records action, observation, and termination events.
    """

    if not isinstance(question, str) or not question.strip():
        raise ReActLoopError("question cannot be empty")

    if max_steps < 1:
        raise ReActLoopError("max_steps must be at least 1")

    if not isinstance(plan, list):
        raise ReActLoopError("plan must be a list")

    trace: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []

    step = 0
    final_answer: str | None = None

    while True:
        if step >= max_steps:
            result = terminate(
                "step_limit",
                current_step=max_steps,
                max_steps=max_steps,
            )

            trace.append(
                {
                    "event": "termination",
                    "reason": result.reason,
                    "step": step,
                }
            )

            return LoopResult(
                status="stopped",
                final_answer=None,
                steps=step,
                observations=observations,
                trace=trace,
            )

        if step >= len(plan):
            result = terminate(
                "failed",
                final_answer="ReAct plan ended without a final answer.",
                current_step=step,
                max_steps=max_steps,
            )

            trace.append(
                {
                    "event": "termination",
                    "reason": result.reason,
                    "step": step,
                }
            )

            return LoopResult(
                status="failed",
                final_answer=result.reason,
                steps=step,
                observations=observations,
                trace=trace,
            )

        step += 1

        item = plan[step - 1]

        action_name = item.get("action")
        args = item.get("args", {})

        try:
            action = select_action(
                action_name=action_name,
                args=args,
                tools=tools,
            )

            validate_action_arguments(
                action,
                item.get("required_arguments", {}),
            )

            trace.append(
                {
                    "event": "action",
                    "step": step,
                    "action": action.name,
                    "args": action.args,
                }
            )

        except (ActionSelectionError, AttributeError) as exc:
            observation = tool_result_to_observation(
                tool_name=str(action_name),
                error=str(exc),
            )

            observations.append(
                {
                    "source": observation.source,
                    "content": observation.content,
                    "success": observation.success,
                }
            )

            trace.append(
                {
                    "event": "observation",
                    "step": step,
                    "source": observation.source,
                    "content": observation.content,
                    "success": observation.success,
                }
            )

            continue

        try:
            tool = tools[action.name]
            result_value = tool(**action.args)

            observation = tool_result_to_observation(
                tool_name=action.name,
                result=result_value,
            )

        except Exception as exc:
            observation = tool_result_to_observation(
                tool_name=action.name,
                error=str(exc),
            )

        observations.append(
            {
                "source": observation.source,
                "content": observation.content,
                "success": observation.success,
            }
        )

        trace.append(
            {
                "event": "observation",
                "step": step,
                "source": observation.source,
                "content": observation.content,
                "success": observation.success,
            }
        )

        if observation.success and "final_answer" in item:
            final_answer = item["final_answer"]

            result = terminate(
                "completed",
                final_answer=final_answer,
                current_step=step,
                max_steps=max_steps,
            )

            trace.append(
                {
                    "event": "termination",
                    "reason": result.reason,
                    "step": step,
                }
            )

            return LoopResult(
                status="completed",
                final_answer=final_answer,
                steps=step,
                observations=observations,
                trace=trace,
            )

        if not can_continue(
            current_step=step,
            max_steps=max_steps,
        ):
            result = terminate(
                "step_limit",
                current_step=max_steps,
                max_steps=max_steps,
            )

            trace.append(
                {
                    "event": "termination",
                    "reason": result.reason,
                    "step": step,
                }
            )

            return LoopResult(
                status="stopped",
                final_answer=None,
                steps=step,
                observations=observations,
                trace=trace,
            )