# HW3 Writeup

Name: 

## Part 1: Wikipedia tool

### Output

Paste the output of `uv run python external_tool.py`.

```

```

### Why return an error message?

Explain in 2-4 sentences why your tool returns an error message instead of raising an exception when the caller is a model in an agent loop.


## Part 2: MCP server

### 1. Client output

Paste the full output of `uv run python mcp_client.py`.

```

```

### 2. Tool choice

For each demo question, state which tool the model chose and whether it was correct. Quote the phrase from your description that steered the choice. If the model chose wrong while you were working, say what you changed.

**Question 1: How tall is the Comcast Technology Center?**


**Question 2: How does an agent decide between thinking and taking an action?**


**Question 3: Who was Alan Turing?**


### 3. Your own question

Paste the output of `uv run python mcp_client.py "your question"` and explain in 2-4 sentences why the model chose that tool.

```

```


### 4. Lifecycle

In 4-6 sentences, explain what `mcp_client.py` does in steps 1-5. Include why the client can call your tools without importing `mcp_server.py`, and why the client is `async`.


## Part 3: Writeup

### Why MCP over hardcoded functions

Give two concrete advantages you experienced in this assignment.


### A tool schema

Show one schema you wrote. Explain what makes it good and what breaks downstream when a description is vague.

