# HW3: Tool Calling & MCP

**CIS 1990**  
**Due:** Week 9, Friday at 11:59 PM  
**Course grade:** 15%

## Purpose

In HW1 and HW2, your tools lived inside your agent's own Python process: the
agent imported `tools.py` or `retriever.py` and called the functions directly.
Real agents usually use tools that live *somewhere else*: another team's
service, a third-party API, a server running on another machine. They reach
those tools through a shared protocol. That protocol is the **Model Context
Protocol (MCP)**, the thing this course is named around.

In this assignment you will:

1. Turn a real external API (Wikipedia) into a tool that returns clean,
   model-friendly text.
2. Expose that tool and your HW2 search + retrieval tools from an **MCP
   server**, with descriptions good enough that a model picks the right tool.
3. Connect to your server with a provided MCP client and explain what you see.

This is the last layer before the final project. The coding is deliberately
small. You edit **only two files**, `external_tool.py` and `mcp_server.py`.
Most of the points are for tool design and for explaining how MCP works.

## Generative AI policy

Generative AI tools, including ChatGPT, Claude, and GitHub Copilot, may be used
only for general questions about course concepts or programming language
features. For example, you may ask what a Python decorator is or what an error
message means.

You may not ask an AI tool to write, complete, debug, design, or solve any part
of this homework. This includes code, tool descriptions, writeup text, and
answers to the short questions. You are responsible for all implementation and
reasoning in your submission.

## Learning objectives

By completing this assignment, you should be able to:

1. Explain MCP's client/server architecture and why a protocol beats
   hardcoding tools into one program.
2. Turn raw API data into a clean tool result, including the error cases.
3. Write typed tool schemas and descriptions that a model can call reliably.
4. Serve existing Python functions as MCP tools and call them from an MCP
   client.

## What we provide

All files are directly in this `hw3/` directory:

```
hw3/
├── README.md            # this handout
├── external_tool.py     # Part 1 TODO: format a Wikipedia summary
├── mcp_server.py        # Part 2 TODO: register three MCP tools
├── mcp_client.py        # provided: connects to your server and calls tools
├── retriever.py         # provided: keyword_search() and retrieve() from HW2
├── ingest.py            # provided: builds index.json for retrieve()
├── embeddings.py        # provided: Gemini embeddings + cosine (from HW2)
├── llm.py               # provided: cached Gemini client (from HW1/HW2)
├── data/corpus/         # five short local documents
└── writeup.md           # your written answers
```

**You only edit `external_tool.py`, `mcp_server.py`, and `writeup.md`.**
Every other file is complete and working. You do not need to copy anything
from HW1 or HW2. Read the provided files anyway, especially `retriever.py` and
`mcp_client.py`, because Part 2 asks you to describe and use them.

The local corpus is intentionally tiny. It covers CIS 1990 course logistics,
LLM agents / RAG / MCP, the University of Pennsylvania, Philadelphia, and
Paris. Anything outside those topics (for example, "Who was Alan Turing?")
can only be answered by the Wikipedia tool.

## Setup

You need Python 3.10 or newer (the `mcp` package requires it), `uv`, and the
same `GEMINI_API_KEY` you used in HW1 and HW2. If you need to install `uv`
or get a key, follow the setup section of the HW1 README.

Open a terminal in the `hw3/` directory and run:

```bash
uv sync
cp .env.example .env
```

On Windows PowerShell, use:

```powershell
Copy-Item .env.example .env
```

Put your `GEMINI_API_KEY` in `.env`. Then verify the setup and build the
vector index (this embeds the corpus once and caches the result):

```bash
uv run python -c "import embeddings, external_tool, llm, retriever; print('Setup OK')"
uv run python ingest.py
uv run python retriever.py
```

`retriever.py` should print a keyword match about the Comcast Technology
Center and two retrieved chunks about agents. If it does, your environment is
ready.

Keep the cache enabled. The provided `llm.py` and `embeddings.py` cache every
response and handle rate limits, so rerunning the client does not spend extra
API quota.

## Background: MCP in five minutes

An **MCP server** is a program that offers tools. An **MCP client** is the
program that uses them (an agent, Claude Desktop, an IDE). They talk over a
connection. In this homework the connection is **stdio**: the client starts the
server as a subprocess and they exchange JSON messages over its
stdin/stdout.

Every MCP session follows the same lifecycle:

| Step | Client call | What happens |
|---|---|---|
| 1 | `stdio_client(params)` | Launches `mcp_server.py` as a subprocess and connects to its stdin/stdout. |
| 2 | `ClientSession(read, write)` | Wraps those two streams in the MCP protocol. |
| 3 | `initialize()` | Handshake: client and server agree on a protocol version and capabilities. |
| 4 | `list_tools()` | The server replies with every tool's **name**, **description**, and **input schema**. |
| 5 | `call_tool(name, args)` | The server runs the tool and returns its result as text. |

The important idea is step 4. The client never imports your Python code. It
learns what your tools are, what they take, and when to use them **only** from
what `list_tools()` returns. When a model is choosing a tool, that
description is the only thing it has to go on.

With the `FastMCP` library, you never write a schema by hand. You decorate an
ordinary typed function, and FastMCP builds the schema from it:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers exactly. Use for arithmetic instead of computing
    in your head. Pass both numbers as integers."""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

| Python | What the client sees |
|---|---|
| function name `add` | tool name `"add"` |
| type hints `a: int, b: int` | input schema `{"a": {"type": "integer"}, "b": {"type": "integer"}}`, both required |
| docstring | tool description |

---

## Part 1: Format a Wikipedia tool result, 15 points

### What is provided

`external_tool.py` already contains `fetch_summary(title)`, which does all of
the networking. It calls the Wikipedia REST API
(`https://en.wikipedia.org/api/rest_v1/page/summary/<title>`), parses the
JSON reply, and catches every network error. **You do not need to know how
HTTP or web scraping works.** `fetch_summary` always returns a Python
dictionary.

On success, the dictionary looks like this (trimmed to the fields you need):

```python
{
    "type": "standard",
    "title": "Alan Turing",
    "description": "English computer scientist (1912-1954)",
    "extract": "Alan Mathison Turing was an English mathematician and ...",
    "content_urls": {
        "desktop": {"page": "https://en.wikipedia.org/wiki/Alan_Turing"}
    },
}
```

On failure, it has a single `"error"` key:

```python
{"error": "not_found"}        # the page does not exist
{"error": "timed out"}        # any other problem: no internet, timeout, ...
```

Not every page has every field. `"description"` and `"content_urls"` are
sometimes missing, and `"type"` is `"disambiguation"` when a title could mean
several pages (for example, `"Mercury"` could be a planet, an element, or a
Roman god).

### Required implementation

Implement `wikipedia_summary(title)` in `external_tool.py`. It must always
return a string and never raise. Handle these cases in this order:

| Case | Return |
|---|---|
| `title` is empty or only spaces | A message asking for a title. **Do not call `fetch_summary`.** |
| `"error"` is `"not_found"` | A "no Wikipedia page found" message that includes the title. |
| any other `"error"` | A "could not reach Wikipedia" message that includes the title. |
| `"type"` is `"disambiguation"` | A message that includes the title and the word **"ambiguous"**. |
| `"extract"` is missing or empty | A "no summary available" message that includes the title. |
| success | The three-line format below. |

The success format is:

```
Alan Turing - English computer scientist (1912-1954)
Alan Mathison Turing was an English mathematician and ...
Source: https://en.wikipedia.org/wiki/Alan_Turing
```

- Line 1 is the page's `title`, then ` - ` and the `description`. If there is
  no description, line 1 is just the title.
- Line 2 is the `extract`.
- Line 3 is `Source: ` and the page URL. If there is no URL, leave this line
  out entirely.
- The word `None` must never appear in your output.

Two Python tools make this easy:

- `data.get("description")` returns `None` instead of crashing when the key is
  missing, so you can check `if description:`.
- For the nested URL, chain `.get()` calls with an empty-dict default:
  `data.get("content_urls", {}).get("desktop", {}).get("page")`.

Test your work with:

```bash
uv run python external_tool.py
```

It tries a real page, a missing page, and an ambiguous title.

### Written answer, in `writeup.md`

1. Paste the output of `uv run python external_tool.py`.
2. In 2-4 sentences: your tool returns an error *message* instead of raising
   an exception. Why is that the right choice when the caller is a model in an
   agent loop rather than a human running a script?

### Grading rubric

**A. Success formatting, 6 points** (autograder)

- 4 points: the output contains the page title and the full extract.
- 1 point: the description and the `Source:` URL appear when present.
- 1 point: missing description or URL is left out cleanly (no `None`).

**B. Error cases, 6 points** (autograder)

- 2 points: a missing page (404) returns a message with the title.
- 1 point: a network error or timeout returns a message with the title.
- 1 point: a disambiguation page returns an "ambiguous" message.
- 1 point: a missing extract returns a message, not `None`.
- 1 point: a blank title returns a message without calling the API.

**C. Written answer, 3 points** (hand-graded)

- 1 point: actual output from your run is pasted.
- 2 points: a correct explanation of why tools should return errors as text.

## Part 2: MCP server, 70 points

### Required implementation

In `mcp_server.py`, use `@mcp.tool()` to register **exactly three tools**
with these names and arguments:

| Tool | Argument | Wraps (already imported for you) | Notes |
|---|---|---|---|
| `search` | `query: str` | `_keyword_search(query)` | Exact keyword match over the corpus. Already returns a string. |
| `retrieve` | `query: str` | `_retrieve(query, k=3)` | Semantic search over the corpus. Returns a **list** of strings, so join them into one string. |
| `wikipedia_summary` | `title: str` | `_wikipedia_summary(title)` | Your Part 1 tool. |

Each tool body should be a single line that calls the provided function. The
real logic already lives in `retriever.py` and `external_tool.py`. Keeping the
logic in plain functions and using `mcp_server.py` only as a thin wrapper is
good design: you can test the logic without MCP, and you can expose it over
MCP without changing it. The finished file is well under 35 lines of code.

Annotate every argument and the return type (`-> str`). FastMCP turns those
type hints into the input schema the client sees.

Do not add `print()` calls to `mcp_server.py`. The client and server talk over
stdout, so anything you print corrupts the protocol messages.

### Writing the descriptions

The docstring of each tool is its **description**, and it is the most
important thing you write in this assignment. A model choosing between your
three tools sees only the names, the argument types, and these descriptions.
`search` and `retrieve` search the *same* documents, so a vague description
like "Searches the documents." gives the model no way to choose between them.

Each description should tell the model:

1. **What the tool can reach.** The local corpus or the live internet? Which
   topics?
2. **When to choose it over the other two.** For example, exact names and
   numbers vs. ideas phrased in different words vs. general knowledge.
3. **What to pass in.** A few keywords? The full question? An exact article
   title?

Aim for 2-4 sentences each.

### Run the provided client

Once your server is written, run:

```bash
uv run python mcp_client.py
```

The client launches your server and walks through the five lifecycle steps
above. It prints the tools your server advertises and calls
`wikipedia_summary("Alan Turing")` directly. Then, for three demo questions,
it gives a Gemini model your tool list and lets the **model** choose which tool
to call and with what arguments:

1. "How tall is the Comcast Technology Center?" (an exact name in the corpus)
2. "How does an agent decide between thinking and taking an action?" (an idea
   in the corpus, worded differently than the document)
3. "Who was Alan Turing?" (not in the corpus at all)

If the model picks the wrong tool, the fix is almost always in your
description, not in the client. You can also try your own question:

```bash
uv run python mcp_client.py "What is the population of Paris?"
```

If the client fails before printing the tool list, the problem is in
`mcp_server.py`. Read the error printed above the traceback, and make sure
`uv run python -c "import mcp_server"` runs cleanly.

### Written answers, in `writeup.md`

1. **Client output.** Paste the full output of `uv run python mcp_client.py`.
2. **Tool choice.** For each of the three demo questions, state which tool the
   model chose and whether it was the right one. Quote the phrase from your
   description that you think steered the choice. If the model chose wrong at
   any point while you were working, say what you changed in the description
   to fix it.
3. **Your own question.** Run the client with one question of your own that
   should go to a different tool than the model first picked, or that sits
   between two tools (for example, a question about Penn that Wikipedia
   could also answer). Paste the output and explain in 2-4 sentences why
   the model chose what it did.
4. **Lifecycle.** In your own words, in 4-6 sentences, explain what
   `mcp_client.py` does in steps 1-5. Your answer should explain why the
   client can call your tools without ever importing `mcp_server.py`, and why
   the client code is `async`.

### Grading rubric

**A. Tool registration, 15 points** (autograder)

- 15 points: the server imports cleanly and registers tools named exactly
  `search`, `retrieve`, and `wikipedia_summary`.

**B. Typed schemas, 10 points** (autograder)

- 10 points: `search` and `retrieve` take a required string `query`, and
  `wikipedia_summary` takes a required string `title`.

**C. Tools call the provided logic, 10 points** (autograder)

- 4 points: `wikipedia_summary` returns your Part 1 output.
- 3 points: `search` returns `_keyword_search`'s result.
- 3 points: `retrieve` returns the retrieved chunks joined into one string,
  not a Python list printed as text.

**D. Descriptions, 20 points**

- 5 points (autograder): every tool has a real description (at least 40
  characters, no `TODO`).
- 15 points (hand-graded), 5 per tool: the description says what the tool
  can reach, when to choose it over the other two tools, and what argument to
  pass. `search` and `retrieve` must be clearly distinguishable.

**E. Client run and written answers, 15 points** (hand-graded)

- 3 points: actual client output pasted, showing all three tools and the
  Wikipedia result.
- 4 points: tool-choice analysis for the three demo questions, with quoted
  description phrases.
- 3 points: your own question, with output and explanation.
- 5 points: lifecycle explanation covers launch, session, handshake, tool
  discovery, and tool calls, plus why no import is needed and why it is async.

## Part 3: Writeup, 15 points

Answer in `writeup.md`:

1. Why MCP instead of hardcoded in-process functions? Give two concrete
   advantages you actually experienced in this assignment.
2. Show one tool schema you wrote and explain what makes it good. What breaks
   downstream when a schema's description is vague?

### Grading rubric

- 8 points: MCP vs. hardcoded functions, with real reasoning tied to your own
  work.
- 7 points: schema-quality analysis.

## Submission checklist

Submit through GitHub Classroom and Gradescope:

- `external_tool.py` and `mcp_server.py`, completed, and
- `writeup.md`, containing all written answers.

Do not submit `.env` (it contains your API key and is ignored by git).

Before submitting, run:

```bash
uv run python external_tool.py
uv run python -c "import mcp_server; print('Server imports OK')"
uv run python mcp_client.py
```

Confirm that the client lists all three tools, that the model's tool choices
are pasted into `writeup.md`, and that every written answer is in your own
words.

The autograder tests Part 1 with the network mocked, and tests that your MCP
server registers the three tools with typed arguments and calls the provided
functions. Descriptions and all written answers are hand-graded.

**Total: 100 points.** Part 1 is 15 points, Part 2 is 70 points, and Part 3 is
15 points. Together these 100 points are converted to the 15% course-grade
weight.
