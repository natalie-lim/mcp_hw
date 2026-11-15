"""Reference solution. mcp_server.py - Part 2: expose three tools over MCP.

Run directly to serve over stdio:  python mcp_server.py
The tool logic lives in retriever.py and external_tool.py; MCP just wraps it.
"""
from mcp.server.fastmcp import FastMCP

from external_tool import wikipedia_summary as _wikipedia_summary
from retriever import keyword_search as _keyword_search
from retriever import retrieve as _retrieve

mcp = FastMCP("cis1990-hw3")


@mcp.tool()
def search(query: str) -> str:
    """Exact keyword search over the local corpus (CIS 1990 course logistics,
    LLM agents/RAG/MCP, Penn, Philadelphia, Paris). Use FIRST when the question
    names a specific thing to match word-for-word: a building, course code,
    number, or proper noun. Pass a few distinctive keywords, not a sentence."""
    return _keyword_search(query)


@mcp.tool()
def retrieve(query: str) -> str:
    """Semantic (embedding) search over the same local corpus. Use when the
    question is about an idea or uses different wording than the documents
    might, e.g. "how does an agent decide what to do next". Pass the full
    question. Returns the 3 most similar passages."""
    return "\n\n".join(_retrieve(query, k=3))


@mcp.tool()
def wikipedia_summary(title: str) -> str:
    """Live Wikipedia lookup for general knowledge NOT in the local corpus
    (people, places, events, concepts). Pass an exact article title such as
    "Alan Turing", not a question."""
    return _wikipedia_summary(title)


if __name__ == "__main__":
    mcp.run()
