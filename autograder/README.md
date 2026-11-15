# HW3 autograder (Gradescope)
Fully offline: urlopen and the embedding API are mocked.

- Part 1 (12 of 15 pts): `wikipedia_summary` formatting and every error case.
- Part 2 (40 of 70 pts): the MCP server registers `search` / `retrieve` /
  `wikipedia_summary`, with required string args (`query` / `query` / `title`)
  and non-placeholder descriptions, and each tool calls through to the
  provided function. Runs on Python 3.10+; auto-skips below that.

**52 of 100 pts autograded.** Hand-graded: the Part 1 written answer (3),
description quality (15), client output and short answers (15), and the
Part 3 writeup (15).

**The Gradescope image must be Python 3.10+** (the `mcp` package requires it)
so the server tests run.

Package: `zip -r hw3-autograder.zip gs_shim.py tests_hw3.py run_tests.py setup.sh run_autograder`
Local:   `TARGET=../solution python3 run_tests.py`

## Grading notes for staff
- Students edit only `external_tool.py` and `mcp_server.py`. Everything else,
  including `mcp_client.py` and the `keyword_search`/`retrieve` logic in
  `retriever.py`, is provided. If the provided client fails, the fault is
  almost always in the student's `mcp_server.py`. Keep a known-good minimal
  server on hand to help isolate it.
- Reward good schema *descriptions*. A vague description is the #1 cause of
  the model calling a tool wrong, and the client's model-routing step makes
  that visible in the pasted output. `search` and `retrieve` cover the same
  corpus, so their descriptions must say how to choose between them.
- Part 1 must handle a missing Wikipedia page gracefully. A real API *will*
  fail during the demo.
