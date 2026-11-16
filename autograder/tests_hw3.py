"""
HW3 autograder. Fully offline: the network and the embedding API are mocked.

  Wikipedia (0 pts): external_tool.wikipedia_summary is provided
      infrastructure and is regression-tested offline. urlopen is mocked.
  Part 1 MCP (50 pts): mcp_server registers search / retrieve /
      wikipedia_summary with typed string args and non-placeholder
      descriptions, and each tool calls through to the provided function.
      Needs Python 3.10+ (the `mcp` package); auto-skips otherwise.

Hand-graded: the five open-ended MCP and agent-design answers in writeup.md
(50 points).
"""
import asyncio
import importlib
import json
import os
import sys
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from gs_shim import weight

os.environ.setdefault("GEMINI_API_KEY", "test-key-not-real")

TURING = {
    "type": "standard",
    "title": "Alan Turing",
    "description": "English computer scientist (1912-1954)",
    "extract": "Alan Mathison Turing was an English mathematician.",
    "content_urls": {"desktop": {"page": "https://en.wikipedia.org/wiki/Alan_Turing"}},
}


def _fresh(name):
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


def _fake_response(payload):
    """A stand-in for urlopen's context-manager response."""
    fake = MagicMock()
    fake.read.return_value = json.dumps(payload).encode()
    fake.__enter__.return_value = fake
    fake.__exit__.return_value = False
    return fake


def _summary(title, payload=None, side_effect=None):
    ext = _fresh("external_tool")
    kwargs = {"side_effect": side_effect} if side_effect else {
        "return_value": _fake_response(payload)}
    with patch("urllib.request.urlopen", **kwargs) as mocked:
        out = ext.wikipedia_summary(title)
    return out, mocked


class TestWikipediaRegression(unittest.TestCase):
    @weight(0)
    def test_formats_title_and_extract(self):
        out, _ = _summary("Alan Turing", TURING)
        self.assertIsInstance(out, str)
        self.assertIn("Alan Turing", out)
        self.assertIn("Alan Mathison Turing was an English mathematician.", out)

    @weight(0)
    def test_includes_description_and_source(self):
        out, _ = _summary("Alan Turing", TURING)
        self.assertIn("English computer scientist", out)
        self.assertIn("Source: https://en.wikipedia.org/wiki/Alan_Turing", out)

    @weight(0)
    def test_optional_fields_missing(self):
        bare = {"type": "standard", "title": "Bare Page", "extract": "Just text."}
        out, _ = _summary("Bare Page", bare)
        self.assertIn("Just text.", out)
        self.assertNotIn("None", out, "missing description/URL should be left out")
        self.assertNotIn("Source:", out)

    @weight(0)
    def test_handles_404(self):
        err = urllib.error.HTTPError("url", 404, "Not Found", {}, None)
        out, _ = _summary("Not A Real Page 99999", side_effect=err)
        self.assertIsInstance(out, str)
        self.assertIn("Not A Real Page 99999", out)

    @weight(0)
    def test_handles_network_error(self):
        out, _ = _summary("Alan Turing", side_effect=TimeoutError("timed out"))
        self.assertIsInstance(out, str)
        self.assertIn("Alan Turing", out)
        self.assertNotIn("Alan Mathison", out)

    @weight(0)
    def test_disambiguation(self):
        page = {"type": "disambiguation", "title": "Mercury",
                "extract": "Mercury may refer to:"}
        out, _ = _summary("Mercury", page)
        self.assertIn("ambiguous", out.lower())
        self.assertIn("Mercury", out)

    @weight(0)
    def test_missing_extract(self):
        out, _ = _summary("Empty Page", {"type": "standard", "title": "Empty Page"})
        self.assertIsInstance(out, str)
        self.assertIn("Empty Page", out)
        self.assertNotIn("None", out)

    @weight(0)
    def test_blank_title_skips_network(self):
        out, mocked = _summary("   ", TURING)
        self.assertIsInstance(out, str)
        self.assertTrue(out.strip())
        mocked.assert_not_called()


def _run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def _call_result_text(result):
    """FastMCP.call_tool's return shape differs across mcp 1.x releases:
    a list of content blocks, or a (blocks, structured) tuple."""
    if isinstance(result, tuple):
        result = result[0]
    return "\n".join(getattr(block, "text", "") for block in result)


EXPECTED = {"search": "query", "retrieve": "query", "wikipedia_summary": "title"}


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        try:
            self.server = _fresh("mcp_server")
        except ImportError as e:
            # Skip only when the `mcp` package itself is missing (Python < 3.10).
            # A missing or broken mcp_server.py must fail, not skip: "mcp" is
            # also a substring of "No module named 'mcp_server'".
            if e.name == "mcp" or (e.name or "").startswith("mcp."):
                self.skipTest(f"`mcp` not importable in this environment: {e}")
            raise
        self.tools = {t.name: t for t in _run(self.server.mcp.list_tools())}

    @weight(15)
    def test_registers_three_tools(self):
        for name in EXPECTED:
            self.assertIn(name, self.tools, f"MCP server must register '{name}'")
        extra = sorted(set(self.tools) - set(EXPECTED))
        if extra:
            self.fail(f"MCP server must register exactly three tools; remove {extra}")

    @weight(10)
    def test_typed_string_arguments(self):
        for name, arg in EXPECTED.items():
            self.assertIn(name, self.tools)
            schema = self.tools[name].inputSchema
            props = schema.get("properties", {})
            self.assertIn(arg, props, f"'{name}' must take an argument named '{arg}'")
            self.assertEqual(props[arg].get("type"), "string",
                             f"'{name}.{arg}' must be annotated as str")
            self.assertIn(arg, schema.get("required", []),
                          f"'{name}.{arg}' must be required")

    @weight(15)
    def test_descriptions_written(self):
        for name in EXPECTED:
            self.assertIn(name, self.tools)
            desc = (self.tools[name].description or "").strip()
            self.assertGreaterEqual(len(desc), 40,
                                    f"'{name}' needs a real docstring description")
            self.assertNotIn("TODO", desc)

    @weight(3)
    def test_wikipedia_tool_calls_through(self):
        with patch("urllib.request.urlopen", return_value=_fake_response(TURING)):
            out = _call_result_text(_run(self.server.mcp.call_tool(
                "wikipedia_summary", {"title": "Alan Turing"})))
        self.assertIn("Alan Mathison Turing", out)

    @weight(3)
    def test_search_tool_calls_keyword_search(self):
        out = _call_result_text(_run(self.server.mcp.call_tool(
            "search", {"query": "Comcast Technology Center"})))
        self.assertIn("1,121", out)

    @weight(4)
    def test_retrieve_tool_joins_chunks(self):
        retriever = sys.modules["retriever"]
        fake_index = [
            {"text": "chunk about agents", "source": "a.txt", "vector": [1.0, 0.0]},
            {"text": "chunk about paris", "source": "b.txt", "vector": [0.0, 1.0]},
        ]
        with patch.object(retriever, "_load_index", return_value=fake_index), \
             patch.object(retriever, "embed", return_value=[[1.0, 0.1]]):
            out = _call_result_text(_run(self.server.mcp.call_tool(
                "retrieve", {"query": "agents"})))
        self.assertIn("chunk about agents", out)
        self.assertNotIn("[", out.split("chunk about agents")[0],
                         "retrieve should return joined text, not a Python list")


if __name__ == "__main__":
    unittest.main()
