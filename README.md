# HW3: Tool Calling & MCP

**CIS 1990**  

## Purpose

Earlier assignments called tools directly inside the agent's Python process.
Real agents often use tools owned by another service, team, or machine. The
**Model Context Protocol (MCP)** gives those tools a standard client/server
interface.

This assignment has two equally weighted parts:

1. **MCP implementation (50 points):** expose the provided local search tools
   and Wikipedia demonstration tool through an MCP server.
2. **Open-ended MCP and agent design (50 points):** reason about protocols,
   schemas, tool selection, reliability, security, and agent architecture.

Wikipedia tools are iplemented for you and provided. Its implementation is complete, and
students are not expected to debug networking, API responses, or formatting.
The only student code file is `mcp_server.py`; written answers go in
`writeup.md`.

## Generative AI policy

Generative AI tools, including ChatGPT, Claude, and GitHub Copilot, may be
used only for general questions about course concepts or programming language
features. For example, you may ask what a Python decorator is or what an
error message means.

You may not ask an AI tool to write, complete, debug, design, or solve any
part of this homework. This includes code, tool descriptions, writeup text,
and answers to the open-ended questions. You are responsible for all
implementation and reasoning in your submission.

## Learning objectives

By completing this assignment, you should be able to:

1. Explain the MCP client/server architecture and why a protocol is useful.
2. Expose ordinary Python functions as typed MCP tools.
3. Design descriptions and schemas that help an agent select tools correctly.
4. Analyze reliability, security, evaluation, and planning in tool-using
   agents.

## Repository

```
hw3/
├── README.md
├── external_tool.py     # provided Wikipedia demonstration tool
├── mcp_server.py        # TODO: register three MCP tools
├── mcp_client.py        # provided MCP client and model router
├── retriever.py         # provided keyword and semantic search
├── ingest.py            # provided vector-index builder
├── embeddings.py        # provided Gemini embeddings and cache
├── llm.py               # provided cached Gemini client
├── data/corpus/         # five short local documents
└── writeup.md           # your written answers
```

Do not edit the provided logic in `external_tool.py`, `retriever.py`, or
`mcp_client.py`. You may inspect them to understand the interfaces.

## Setup

You need Python 3.10+, `uv`, and the `GEMINI_API_KEY` used in earlier
assignments.

```bash
uv sync
cp .env.example .env
uv run python -c "import mcp_server; print('Setup OK')"
uv run python ingest.py
```

On Windows PowerShell:

```powershell
uv sync
Copy-Item .env.example .env
uv run python -c "import mcp_server; print('Setup OK')"
uv run python ingest.py
```

The embedding and model helpers cache responses locally. Do not submit `.env`,
`.cache/`, `.ecache/`, or `index.json`.

## MCP background

An MCP server offers tools. An MCP client connects to it, discovers its tools,
and calls them through a shared protocol. In this assignment the transport is
stdio: the client launches `mcp_server.py` as a subprocess and communicates
through its stdin and stdout.

The lifecycle is:

1. `stdio_client()` launches the server.
2. `ClientSession` wraps the streams in MCP.
3. `initialize()` performs the protocol handshake.
4. `list_tools()` returns names, descriptions, and input schemas.
5. `call_tool()` sends a tool name and arguments and receives the result.

The client does not import `mcp_server.py`. It learns the available interface
from the protocol response. FastMCP builds the schema from Python type hints
and uses each function's docstring as its description:

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers exactly."""
    return a + b
```

Do not print from `mcp_server.py`; stdout carries protocol messages.

## Part 1: MCP implementation: 50 points

In `mcp_server.py`, register exactly these three tools with `@mcp.tool()`:

| Tool | Argument | Wraps | Return |
|---|---|---|---|
| `search` | `query: str` | `_keyword_search(query)` | `str` |
| `retrieve` | `query: str` | `_retrieve(query, k=3)` | `str` |
| `wikipedia_summary` | `title: str` | `_wikipedia_summary(title)` | `str` |

The `retrieve` wrapper must join its list of passages into one string, for
example with `"\n\n".join(...)`. Each function must have a typed `str`
argument, a `-> str` return annotation, and a 2–4 sentence description.

Descriptions must tell the model:

1. What information the tool can reach.
2. When to choose it over the other tools.
3. What form of argument to provide.

The local corpus covers CIS 1990 logistics, LLM agents, RAG, MCP, Penn,
Philadelphia, and Paris. Use exact keyword search for distinctive names,
numbers, and identifiers; use semantic retrieval for paraphrased questions;
use Wikipedia for general knowledge outside the corpus.

Run the client with:

```bash
uv run python mcp_client.py
```

It advertises the tools, calls Wikipedia directly, and asks Gemini to choose a
tool for three questions. The client is a diagnostic for your schemas and
descriptions, not a separate implementation task.

### MCP rubric

- **15 points:** exactly three correctly named tools are registered.
- **10 points:** required argument names and string schemas.
- **10 points:** wrappers call the provided functions and return the correct
  shape.
- **15 points:** descriptions clearly distinguish tool coverage, selection
  criteria, and argument format.

## Part 2: Open-ended MCP and agent design: 50 points

Answer all questions in `writeup.md` in your own words. Use concrete examples
from this assignment where requested. Strong answers state assumptions,
identify tradeoffs, and explain failure modes rather than only defining terms.

### 1. Protocol architecture: 10 points

Compare MCP with importing ordinary Python functions directly. Give at least
two concrete advantages and one cost or limitation of MCP. Explain how the
client/server boundary changes deployment, versioning, or testing.

### 2. Tool and schema design: 10 points

Choose one of the three tools and show the schema the client receives,
including its name, argument, type, and description. Explain how a vague
description can cause a silent wrong-tool failure. Propose one change that
would make the schema safer or more precise.

### 3. Reliable agent behavior: 10 points

Design a strategy for an agent that must choose among exact search, semantic
retrieval, and an external API. Discuss ambiguity, missing results, malformed
tool arguments, timeouts, retries, and how the agent should decide whether to
try another tool. Include a distinction between tool errors and valid empty
results.

### 4. Security and trust boundaries: 10 points

Identify at least four security or privacy risks in an MCP-based agent. Include
risks involving untrusted tool descriptions or results, prompt injection,
overpowered tools, secrets, or cross-user data. For each, propose a concrete
mitigation and explain what risk remains.

### 5. Novel system design: 10 points

Design an MCP-based agent for a domain not used in this assignment, such as
customer support, software maintenance, scientific research, or healthcare
administration. Specify:

- at least three tools and their input/output contracts;
- which actions require confirmation;
- how the agent handles conflicting or stale information;
- how you would evaluate tool selection and final answers; and
- one failure scenario with a recovery policy.

## Submission

Submit:

- `mcp_server.py`
- `writeup.md`

Before submitting, run:

```bash
uv run python -c "import mcp_server; print('Server imports OK')"
uv run python mcp_client.py
```

Confirm that the client lists exactly three tools and that the writeup answers
all five open-ended questions.
