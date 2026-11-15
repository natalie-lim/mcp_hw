"""
mcp_server.py - Part 2: expose your three tools over MCP.

An MCP server is a small program that advertises a list of tools. Any MCP
client (our provided mcp_client.py, Claude Desktop, an IDE, another team's
agent) can connect, ask "what tools do you have?", read each tool's name,
description, and argument types, and then call them.

FastMCP builds that advertisement for you from ordinary Python functions:

    @mcp.tool()                         <- registers the function as a tool
    def add(a: int, b: int) -> int:     <- name + typed args become the schema
        '''Add two integers. Use for...'''  <- docstring becomes the description
        return a + b

The model never sees your code, only the name, the argument types, and the
docstring. The docstring is how the model decides WHEN to call each tool, so
write it for the model: say what the tool covers, when to choose it over the
other two tools, and what to pass in.

The tool *logic* is already written (retriever.py and external_tool.py). Each
tool here should be a thin wrapper, usually a single line that calls the
imported function. The finished file is well under 35 lines of code.

Test it with the provided client (it starts this file for you):

    uv run python mcp_client.py

IMPORTANT: do not add print() calls to this file. The client talks to this
server over stdin/stdout, so anything printed to stdout corrupts the protocol.
"""
from mcp.server.fastmcp import FastMCP

# The imported functions get a leading underscore so that your tool functions
# below can use the plain names (search, retrieve, wikipedia_summary) without
# overwriting the functions they call.
from external_tool import wikipedia_summary as _wikipedia_summary
from retriever import keyword_search as _keyword_search
from retriever import retrieve as _retrieve

# The server's name is what clients display when they connect.
mcp = FastMCP("cis1990-hw3")


# TODO: register exactly three tools with @mcp.tool(). Use these exact
# function names and argument names, and annotate every argument and return
# type, because FastMCP turns the type hints into the tool's input schema.
#
#   search(query: str) -> str
#       Wrap _keyword_search(query). It already returns a string.
#
#   retrieve(query: str) -> str
#       Wrap _retrieve(query, k=3). It returns a list of strings, and an MCP
#       tool should return one string, so join them, e.g. with "\n\n".
#
#   wikipedia_summary(title: str) -> str
#       Wrap _wikipedia_summary(title) from Part 1.
#
# Give each tool a docstring that tells the model:
#   1. what information the tool can reach (local corpus vs. the internet),
#   2. when to choose it instead of the other two tools, and
#   3. what to pass as the argument (keywords? a full question? a title?).
# The local corpus covers: CIS 1990 course logistics, LLM agents / RAG / MCP,
# the University of Pennsylvania, Philadelphia, and Paris.


if __name__ == "__main__":
    # With no arguments, FastMCP serves over stdio: it reads requests from
    # stdin and writes responses to stdout until the client disconnects.
    mcp.run()
