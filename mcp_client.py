"""
mcp_client.py - PROVIDED MCP client. Run it, read it, don't rewrite it.

This client connects to your mcp_server.py the same way any MCP host would
(Claude Desktop, an IDE, another team's agent). Run it from the hw3/ folder:

    uv run python mcp_client.py                      # the three demo questions
    uv run python mcp_client.py "your own question"  # one question of your own

It walks through the full MCP lifecycle:

    1. stdio_client  launches mcp_server.py as a subprocess and connects to
                     its stdin/stdout.
    2. ClientSession wraps those two streams in the MCP protocol.
    3. initialize()  performs the handshake (protocol version, capabilities).
    4. list_tools()  asks the server what tools it has. The client never
                     imports mcp_server.py, so it learns the tool names,
                     descriptions, and argument schemas only from this reply.
    5. call_tool()   runs one tool on the server and returns its result.

Step 6 is the part that makes it an agent: for each question, the model
reads the tool descriptions from step 4 and picks a tool and arguments. If
your descriptions are vague, this is where you will see the wrong tool get
picked.

Everything is async because each step waits on another process (the server)
to reply. The async/await syntax lets the program pause at each "await"
until the reply arrives.
"""
from __future__ import annotations
import asyncio
import json
import os
import re
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

HERE = Path(__file__).parent

# One question for each tool: an exact name in the local corpus, a
# paraphrased idea from the local corpus, and a fact only Wikipedia has.
DEMO_QUESTIONS = [
    "How tall is the Comcast Technology Center?",
    "How does an agent decide between thinking and taking an action?",
    "Who was Alan Turing?",
]

ROUTER_SYSTEM = (
    "You choose which tool answers a question. You will see a list of tools "
    "with their descriptions and arguments. Pick exactly one tool and reply "
    "with only a JSON object, no other text:\n"
    '{"tool": "<tool name>", "arguments": {"<argument>": "<value>"}}'
)


def _result_text(result) -> str:
    """_result_text - pull the text out of a call_tool result.

    A tool result holds a list of content blocks, because a tool may return
    text, images, or several pieces at once. Our tools return one text block.
    """
    texts = [block.text for block in result.content if hasattr(block, "text")]
    return "\n".join(texts) if texts else "(no text content)"


def _tool_menu(tools) -> str:
    """_tool_menu - describe the advertised tools for the model's prompt.

    The model sees exactly what list_tools() returned: each tool's name, its
    description (your docstring), and its input schema (from your type hints).
    """
    lines = []
    for tool in tools:
        args = ", ".join(f"{name}: {spec.get('type', 'any')}"
                         for name, spec in tool.inputSchema.get("properties", {}).items())
        lines.append(f"- {tool.name}({args}): {tool.description}")
    return "\n".join(lines)


def _choose_tool(question: str, tools) -> dict:
    """_choose_tool - ask the model which tool to call for a question.

    Returns:
        dict: {"tool": name, "arguments": {...}} parsed from the model's reply.
    """
    # Imported here so steps 1-5 still run if the Gemini key is not set yet.
    from llm import complete

    prompt = f"Tools:\n{_tool_menu(tools)}\n\nQuestion: {question}"
    reply = complete(prompt, system=ROUTER_SYSTEM, temperature=0.0)
    # Models sometimes wrap JSON in ```json fences; grab the {...} part.
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise ValueError(f"model did not return JSON: {reply[:120]}")
    return json.loads(match.group(0))


async def main(questions: list[str]) -> None:
    # Step 1: describe how to launch the server. sys.executable is the Python
    # running this client (the uv environment), so the server gets the same
    # installed packages. env passes GEMINI_API_KEY through if you exported it,
    # and hides FastMCP's per-request log lines (errors are still shown).
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(HERE / "mcp_server.py")],
        cwd=str(HERE),
        env={**os.environ, "FASTMCP_LOG_LEVEL": "WARNING"},
    )
    async with stdio_client(params) as (read, write):
        # Step 2: wrap the raw streams in a protocol session.
        async with ClientSession(read, write) as session:
            # Step 3: handshake.
            await session.initialize()

            # Step 4: discover tools.
            tools = (await session.list_tools()).tools
            print("Tools advertised by the server:")
            for tool in tools:
                print(f"  - {tool.name}{tool.inputSchema.get('properties', {})}")
                # Docstrings span several lines; print each one as a single line.
                print(f"      {' '.join((tool.description or '').split())}")

            # Step 5: call one tool directly, with arguments we chose.
            result = await session.call_tool("wikipedia_summary", {"title": "Alan Turing"})
            print("\n[direct call] wikipedia_summary('Alan Turing') ->")
            print(_result_text(result)[:400])

            # Step 6: let the model choose the tool from your descriptions.
            for question in questions:
                print(f"\n[model] Question: {question}")
                try:
                    choice = _choose_tool(question, tools)
                except Exception as error:
                    print(f"  Could not get a tool choice from the model: {error}")
                    continue
                print(f"  Model chose: {choice.get('tool')}({choice.get('arguments')})")
                result = await session.call_tool(choice.get("tool", ""),
                                                 choice.get("arguments", {}))
                print("  Result:", _result_text(result)[:400])


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:] or DEMO_QUESTIONS))
