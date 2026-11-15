# HW3 Writeup

Name:

## 1. Protocol architecture: 10 points

Compare MCP with importing ordinary Python functions directly. Give at least
two concrete advantages and one cost or limitation of MCP. Explain how the
client/server boundary changes deployment, versioning, or testing.


## 2. Tool and schema design: 10 points

Choose one tool from `mcp_server.py` and show the schema the client receives,
including its name, argument, type, and description. Explain how a vague
description can cause a silent wrong-tool failure. Propose one change that
would make the schema safer or more precise.


## 3. Reliable agent behavior: 10 points

Design a strategy for an agent choosing among exact search, semantic
retrieval, and an external API. Discuss ambiguity, missing results, malformed
arguments, timeouts, retries, and when to try another tool. Distinguish tool
errors from valid empty results.


## 4. Security and trust boundaries: 10 points

Identify at least four security or privacy risks in an MCP-based agent.
Include risks involving untrusted tool descriptions or results, prompt
injection, overpowered tools, secrets, or cross-user data. For each, propose a
concrete mitigation and explain what risk remains.


## 5. Novel system design: 10 points

Design an MCP-based agent for a new domain. Specify at least three tools and
their input/output contracts, which actions require confirmation, how stale
or conflicting information is handled, how tool selection and final answers
are evaluated, and one failure scenario with a recovery policy.



How much time did you spend on this assignment?