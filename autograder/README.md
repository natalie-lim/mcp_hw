# HW3 autograder (Gradescope)

Fully offline: urlopen and the embedding API are mocked.

- Wikipedia is provided infrastructure and is regression-tested so changes to
  the starter files do not break the demonstration.
- **Part 1 (50 pts):** the MCP server registers `search`, `retrieve`, and
  `wikipedia_summary` with required string arguments and non-placeholder
  descriptions, and each tool calls through to the provided function.

**50 points are autograded for MCP.** The remaining 50 points are hand-graded
from the five open-ended MCP and agent-design answers in `writeup.md`.

The Gradescope image must be Python 3.10+ because the `mcp` package requires
it. The tests auto-skip MCP checks on older Python versions.

Package:

```bash
zip -r hw3-autograder.zip gs_shim.py tests_hw3.py run_tests.py setup.sh run_autograder
```

Local:

```bash
TARGET=../solution python3 run_tests.py
```

## Grading notes for staff

- Students edit only `mcp_server.py` and `writeup.md`. Everything else,
  including the completed Wikipedia demonstration, `mcp_client.py`, and the
  `keyword_search`/`retrieve` logic in `retriever.py`, is provided.
- Reward good schema descriptions. A vague description is the primary cause
  of wrong tool selection, and the client's model-routing step makes that
  visible.
- Wikipedia is demonstration infrastructure, not a student implementation
  requirement. A real API may fail during the demo; that should not affect
  the MCP implementation score.
