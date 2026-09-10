"""Shared Agent SDK query-and-extract boilerplate.

Every real Agent SDK call in this codebase (narrative.py's synthesis and
judge calls, detection/identity_resolution.py's per-candidate resolution)
needs the same thing: run one query() to completion and pull the result
text back out. Extracts via ResultMessage.result, never by stringifying
raw SDK message objects - see reference/milestone-6-agent-sdk-patterns/
README.md for why that silently breaks.
"""

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query


async def run_query(prompt: str, options: ClaudeAgentOptions) -> tuple[str, float]:
    """Run one query() call to completion. Returns (result text, cost in
    USD). Raises if the run ends without ever producing a ResultMessage -
    a genuine bug (a caller should never see this if the SDK is behaving),
    not something to retry or swallow.
    """
    result_text: str | None = None
    cost_usd = 0.0
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, ResultMessage):
            result_text = message.result
            cost_usd = message.total_cost_usd or 0.0
    if result_text is None:
        raise RuntimeError("Agent run finished without a ResultMessage")
    return result_text, cost_usd
