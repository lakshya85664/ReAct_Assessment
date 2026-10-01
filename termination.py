from __future__ import annotations

from dataclasses import dataclass


class TerminationError(ValueError):
    """Raised when termination rules are violated."""


@dataclass(frozen=True)
class TerminationResult:
    terminated: bool
    reason: str


ALLOWED_REASONS = {
    "completed",
    "failed",
    "step_limit",
    "explicit_stop",
}


def terminate(
    reason: str,
    *,
    final_answer: str | None = None,
    current_step: int = 0,
    max_steps: int = 3,
) -> TerminationResult:
    """
    Determine and validate a terminal ReAct state.

    The function enforces a bounded step limit and requires
    an appropriate terminal reason.
    """

    if reason not in ALLOWED_REASONS:
        raise TerminationError(
            f"invalid termination reason: {reason}"
        )

    if current_step < 0:
        raise TerminationError("current_step cannot be negative")

    if max_steps < 1:
        raise TerminationError("max_steps must be at least 1")

    if current_step > max_steps:
        raise TerminationError(
            "current_step cannot exceed max_steps"
        )

    if reason == "completed":
        if not isinstance(final_answer, str) or not final_answer.strip():
            raise TerminationError(
                "completed termination requires a final answer"
            )

    if reason == "failed":
        if not isinstance(final_answer, str) or not final_answer.strip():
            raise TerminationError(
                "failed termination requires a failure reason"
            )

    if reason == "step_limit" and current_step != max_steps:
        raise TerminationError(
            "step_limit termination requires current_step == max_steps"
        )

    return TerminationResult(
        terminated=True,
        reason=reason,
    )


def can_continue(
    *,
    current_step: int,
    max_steps: int,
    terminated: bool = False,
) -> bool:
    """Return whether another ReAct step is allowed."""

    if terminated:
        return False

    if current_step < 0:
        raise TerminationError("current_step cannot be negative")

    if max_steps < 1:
        raise TerminationError("max_steps must be at least 1")

    return current_step < max_steps