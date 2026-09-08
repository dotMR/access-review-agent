"""Milestone 1: single subagent, AWS only, Orphaned detection.

Wires read_access_data + read_hris through the Agent SDK and asks the
model to reason over the results, rather than hand-writing the anti-join
in Python - proving the tool-to-reasoning pipeline works, even for a
category simple enough that the reasoning itself is trivial.
"""

import json
import re
from pathlib import Path
from typing import Any

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, create_sdk_mcp_server, query

from access_review_agent.tools.access_data import make_read_access_data_tool
from access_review_agent.tools.hris import make_read_hris_tool

SYSTEM_PROMPT = """\
You are the AWS subagent of a joiner-mover-leaver access review agent. \
You only ever reason about AWS access - you have no visibility into any \
other system.

Task: detect Orphaned access. An access record is Orphaned if both are true:
- its employee_id matches an HRIS record whose status is "terminated"
- the access record's own status is "active" (not "revoked")

A contractor whose end_date has passed but whose HRIS status is still \
"active" is NOT Orphaned - that is a different, out-of-scope check. Only \
HRIS status="terminated" counts.

Call read_access_data and read_hris to get the current data. Do not guess \
or assume data you have not actually read.

Respond with your reasoning, then end your reply with a fenced json code \
block matching exactly this shape (empty findings list if none):

```json
{
  "findings": [
    {
      "category": "orphaned",
      "system_name": "aws",
      "employee_id": "<employee_id>",
      "source_record": {"file": "access_aws.csv", "employee_id": "<employee_id>"}
    }
  ]
}
```
"""


def build_options(data_dir: Path) -> ClaudeAgentOptions:
    access_tool = make_read_access_data_tool("aws", data_dir)
    hris_tool = make_read_hris_tool(data_dir)

    server = create_sdk_mcp_server(
        name="access_review",
        version="0.1.0",
        tools=[access_tool, hris_tool],
    )

    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"access_review": server},
        allowed_tools=[
            "mcp__access_review__read_access_data",
            "mcp__access_review__read_hris",
        ],
    )


def extract_json_block(text: str) -> dict[str, Any]:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not match:
        raise ValueError(f"No fenced json block found in model output:\n{text}")
    return json.loads(match.group(1))


async def run_orphaned_check(data_dir: Path) -> dict[str, Any]:
    """Run the AWS Orphaned check against fixture data in data_dir.

    Returns the parsed findings dict extracted from the model's response.
    """
    options = build_options(data_dir)
    result_text: str | None = None
    async for message in query(prompt="Check AWS for orphaned access.", options=options):
        if isinstance(message, ResultMessage):
            result_text = message.result

    if result_text is None:
        raise RuntimeError("Agent run finished without a ResultMessage")

    return extract_json_block(result_text)
