from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


class ReActStateError(ValueError):
    """Raised when a ReAct state operation violates a safety boundary."""


@dataclass
class ReActState:
    """
    State carried through a ReAct loop.

    The state keeps the question, available tools, observations,
    current step, maximum step limit, final answer, and status.
    """

    question: str
    tools: dict[str, Any]
    max_steps: int = 3
    observations: list[str] = field(default_factory=list)
    step: int = 0
    final_answer: str | None = None
    status: str = "running"

    def __post_init__(self) -> None:
        self.question = self.question.strip()

        if not self.question:
            raise ReActStateError("question cannot be empty")

        if not isinstance(self.tools, dict):
            raise ReActStateError("tools must be a dictionary")

        if self.max_steps < 1:
            raise ReActStateError("max_steps must be at least 1")

        if self.step < 0:
            raise ReActStateError("step cannot be negative")

        if self.step > self.max_steps:
            raise ReActStateError("step cannot exceed max_steps")

        allowed_statuses = {"running", "completed", "failed", "stopped"}
        if self.status not in allowed_statuses:
            raise ReActStateError(
                f"invalid status: {self.status}"
            )

    def add_observation(self, observation: str) -> None:
        """Record an observation produced by the environment/tool layer."""

        if not isinstance(observation, str):
            raise ReActStateError("observation must be a string")

        observation = observation.strip()

        if not observation:
            raise ReActStateError("observation cannot be empty")

        self.observations.append(observation)

    def advance(self) -> int:
        """
        Advance the ReAct loop by one step.

        The maximum-step guardrail is enforced here.
        """

        if self.status != "running":
            raise ReActStateError(
                f"cannot advance a state with status={self.status}"
            )

        if self.step >= self.max_steps:
            self.status = "stopped"
            raise ReActStateError("step limit reached")

        self.step += 1
        return self.step

    def complete(self, answer: str) -> None:
        """Mark the ReAct state as successfully completed."""

        if not isinstance(answer, str) or not answer.strip():
            raise ReActStateError("final answer cannot be empty")

        self.final_answer = answer.strip()
        self.status = "completed"

    def fail(self, reason: str) -> None:
        """Record a transparent failure state."""

        if not isinstance(reason, str) or not reason.strip():
            raise ReActStateError("failure reason cannot be empty")

        self.final_answer = reason.strip()
        self.status = "failed"

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable state snapshot for trace evidence."""

        return {
            "question": self.question,
            "tools": sorted(self.tools.keys()),
            "observations": list(self.observations),
            "step": self.step,
            "max_steps": self.max_steps,
            "final_answer": self.final_answer,
            "status": self.status,
        }