from __future__ import annotations

from dataclasses import dataclass


class ObservationError(ValueError):
    """Raised when an observation violates the ReAct observation contract."""


@dataclass(frozen=True)
class Observation:
    """A structured result returned to the ReAct state."""

    source: str
    content: str
    success: bool

    def __post_init__(self) -> None:
        if not isinstance(self.source, str) or not self.source.strip():
            raise ObservationError("observation source cannot be empty")

        if not isinstance(self.content, str) or not self.content.strip():
            raise ObservationError("observation content cannot be empty")

        if not isinstance(self.success, bool):
            raise ObservationError("observation success must be boolean")


def create_observation(
    source: str,
    content: str,
    success: bool = True,
) -> Observation:
    """
    Create a validated observation.

    Tool failures are represented as observations with success=False.
    """

    return Observation(
        source=source.strip(),
        content=content.strip(),
        success=success,
    )


def tool_result_to_observation(
    tool_name: str,
    result: str | None = None,
    error: str | None = None,
) -> Observation:
    """
    Convert either a successful tool result or a tool failure
    into a ReAct observation.

    A tool failure does not crash the ReAct state. It becomes
    an observable failure that the next reasoning step can inspect.
    """

    if not isinstance(tool_name, str) or not tool_name.strip():
        raise ObservationError("tool name cannot be empty")

    if result is not None and error is not None:
        raise ObservationError(
            "result and error cannot both be provided"
        )

    if error is not None:
        if not isinstance(error, str) or not error.strip():
            raise ObservationError("tool error cannot be empty")

        return create_observation(
            source=tool_name,
            content=f"tool_error: {error.strip()}",
            success=False,
        )

    if result is None:
        raise ObservationError(
            "tool result or error is required"
        )

    if not isinstance(result, str) or not result.strip():
        raise ObservationError("tool result cannot be empty")

    return create_observation(
        source=tool_name,
        content=result.strip(),
        success=True,
    )