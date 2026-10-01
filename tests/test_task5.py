from react_loop import run_react_loop


def lookup_order(query: str) -> str:
    return f"verified: {query}"


def failing_lookup(query: str) -> str:
    raise RuntimeError("temporary service unavailable")


TOOLS = {
    "lookup": lookup_order,
    "failing_lookup": failing_lookup,
}


def test_successful_react_loop():
    result = run_react_loop(
        question="Find order 88213",
        tools=TOOLS,
        plan=[
            {
                "action": "lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
                "final_answer": "Order 88213 is verified.",
            }
        ],
        max_steps=3,
    )

    assert result.status == "completed"
    assert result.steps == 1
    assert result.final_answer == "Order 88213 is verified."
    assert result.observations[0]["success"] is True


def test_failure_becomes_observation():
    result = run_react_loop(
        question="Recover from failure",
        tools=TOOLS,
        plan=[
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
                "final_answer": "Recovered successfully.",
            },
        ],
        max_steps=3,
    )

    assert result.status == "completed"
    assert result.steps == 2
    assert result.observations[0]["success"] is False
    assert result.observations[1]["success"] is True


def test_step_limit_stops_loop():
    result = run_react_loop(
        question="Bounded execution",
        tools=TOOLS,
        plan=[
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
            {
                "action": "failing_lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
            },
        ],
        max_steps=2,
    )

    assert result.status == "stopped"
    assert result.steps == 2
    assert result.final_answer is None


def test_trace_contains_action_observation_and_termination():
    result = run_react_loop(
        question="Trace test",
        tools=TOOLS,
        plan=[
            {
                "action": "lookup",
                "args": {"query": "order 88213"},
                "required_arguments": {"query": str},
                "final_answer": "Done.",
            }
        ],
        max_steps=3,
    )

    events = [item["event"] for item in result.trace]

    assert "action" in events
    assert "observation" in events
    assert "termination" in events


def test_invalid_action_becomes_failure_observation():
    result = run_react_loop(
        question="Unknown action",
        tools=TOOLS,
        plan=[
            {
                "action": "unknown_tool",
                "args": {},
            }
        ],
        max_steps=2,
    )

    assert result.status == "failed"
    assert result.observations[0]["success"] is False
    assert "not registered" in result.observations[0]["content"]