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

Package (from the repo root):

```bash
bash autograder/make_zip.sh    # writes autograder/hw3-autograder.zip
```

The zip contains the test harness plus a `provided/` folder with every file
`mcp_server.py` imports (`retriever.py`, `external_tool.py`, `embeddings.py`,
`llm.py`, `ingest.py`, `data/corpus/`). Students submit only `mcp_server.py`
and `writeup.md`, so `run_autograder` builds a clean grading folder from
`provided/` and copies in the student's `mcp_server.py`. Provided files that a
student submits are ignored. Rebuild the zip whenever a provided file changes.

Student starter (upload this to Canvas/Ed):

```bash
bash autograder/make_starter_zip.sh    # writes autograder/hw3-starter.zip
```

It contains only git-tracked files outside `solution/` and `autograder/`.

Local:

```bash
TARGET=../solution python3 run_tests.py
```

## Grading notes for staff

- Students edit only `mcp_server.py` and `writeup.md`. Everything else,
  including the completed Wikipedia demonstration, `mcp_client.py`, and the
  `keyword_search`/`retrieve` logic in `retriever.py`, is provided.
- Descriptions (15 pts) are autograded by a sanity check only: at least 40
  characters and no "TODO". This is deliberate; description quality is not
  hand-graded. A vague description is still the main cause of wrong tool
  selection, and the client's model-routing step makes that visible, so it is
  worth pointing out in feedback.
- Wikipedia is demonstration infrastructure, not a student implementation
  requirement. A real API may fail during the demo; that should not affect
  the MCP implementation score.
