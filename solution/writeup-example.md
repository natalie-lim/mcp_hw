# HW3 Writeup

> **Staff note:** model "A-grade" writeup for grading calibration, not a
> template for students. Grounded in the reference `solution/` files and
> written in first-person student voice. The Part 1 output and the direct
> Wikipedia call are from a real run. The `[model]` routing lines in Part 2
> were produced with the model call stubbed (no API key when this was
> written). **Regenerate them with a real `uv run python mcp_client.py`
> before using this to calibrate.**

Name: Example Student

## Part 1: Wikipedia tool

### Output

```
>>> wikipedia_summary('Alan Turing')
Alan Turing - English computer scientist (1912–1954)
Alan Mathison Turing was an English mathematician and logician widely regarded as the father of theoretical computer science. He formalised the concepts of algorithm and computation with the Turing machine, a model of a general-purpose computer, and his contributions to cryptanalysis helped the Allies of World War II decipher messages encrypted by the German Enigma machine. He also contributed the Turing test to philosophy of artificial intelligence and the Turing pattern concept to mathematical and theoretical biology.
Source: https://en.wikipedia.org/wiki/Alan_Turing

>>> wikipedia_summary('Definitely Not A Real Page 12345')
No Wikipedia page found for 'Definitely Not A Real Page 12345'.

>>> wikipedia_summary('Mercury')
'Mercury' is ambiguous on Wikipedia (it could mean several pages). Try a more specific title.
```

### Why return an error message?

If my tool raised an exception, the whole agent run would crash on the first
bad title, and the model would never find out what went wrong. A returned
string becomes the tool's observation, so the model can read "No Wikipedia
page found for 'Mercury planet'" and retry with a better title, or switch to a
different tool. The "ambiguous" message is the clearest case: it tells the
model exactly what to do next ("try a more specific title").

## Part 2: MCP server

### 1. Client output

```
Tools advertised by the server:
  - search{'query': {'title': 'Query', 'type': 'string'}}
      Exact keyword search over the local corpus (CIS 1990 course logistics, LLM agents/RAG/MCP, Penn, Philadelphia, Paris). Use FIRST when the question names a specific thing to match word-for-word: a building, course code, number, or proper noun. Pass a few distinctive keywords, not a sentence.
  - retrieve{'query': {'title': 'Query', 'type': 'string'}}
      Semantic (embedding) search over the same local corpus. Use when the question is about an idea or uses different wording than the documents might, e.g. "how does an agent decide what to do next". Pass the full question. Returns the 3 most similar passages.
  - wikipedia_summary{'title': {'title': 'Title', 'type': 'string'}}
      Live Wikipedia lookup for general knowledge NOT in the local corpus (people, places, events, concepts). Pass an exact article title such as "Alan Turing", not a question.

[direct call] wikipedia_summary('Alan Turing') ->
Alan Turing - English computer scientist (1912–1954)
Alan Mathison Turing was an English mathematician and logician widely regarded as the father of theoretical computer science. ...

[model] Question: How tall is the Comcast Technology Center?
  Model chose: search({'query': 'Comcast Technology Center'})
  Result: [philadelphia.txt] Philadelphia is the largest city in Pennsylvania. The tallest building in Philadelphia is the Comcast Technology Center, which stands 1,121 feet tall. ...

[model] Question: How does an agent decide between thinking and taking an action?
  Model chose: retrieve({'query': 'How does an agent decide between thinking and taking an action?'})
  Result: An LLM agent is a language model placed inside a loop and given tools to act on the world. The ReAct pattern interleaves reasoning and acting: ...

[model] Question: Who was Alan Turing?
  Model chose: wikipedia_summary({'title': 'Alan Turing'})
  Result: Alan Turing - English computer scientist (1912–1954) ...
```

### 2. Tool choice

**Question 1.** The model chose `search` with just the keywords "Comcast
Technology Center", which is correct: it is an exact proper noun that appears
word-for-word in `philadelphia.txt`. The phrases that steered it were "names
a specific thing to match word-for-word: a building" and "Pass a few
distinctive keywords, not a sentence". The second phrase is why it passed the
building name instead of the whole question.

**Question 2.** The model chose `retrieve` with the full question, which is
correct: the corpus never says "decide between thinking and acting", it says
"the ReAct pattern interleaves reasoning and acting". Keyword search would
only match on "agent". The steering phrase was "uses different wording than
the documents might". My first draft of `retrieve` just said "Vector search
over the corpus", and the model sent this question to `search`. Adding the
example "how does an agent decide what to do next" fixed it.

**Question 3.** The model chose `wikipedia_summary` with the title "Alan
Turing", which is correct, because nothing in the corpus mentions him. The
phrases were "general knowledge NOT in the local corpus" and "Pass an exact
article title ... not a question". Before I added the second phrase it once
passed "Who was Alan Turing" as the title, which returned "No Wikipedia page
found".

### 3. Your own question

```
[model] Question: When was the University of Pennsylvania founded?
  Model chose: search({'query': 'University of Pennsylvania founded'})
  Result: [penn.txt] The University of Pennsylvania is an Ivy League university in Philadelphia, founded in 1740. ...
```

Wikipedia could also answer this, but the model chose `search` because my
`search` description lists "Penn" as a corpus topic and the question names a
proper noun. That is the behavior I want: the local corpus is the trusted
source for its own topics, and Wikipedia is only for what the corpus lacks.
If I removed "Penn" from the topic list, I would expect the model to go to
Wikipedia instead.

### 4. Lifecycle

`stdio_client` launches my `mcp_server.py` as a subprocess and hands back a
read stream and a write stream connected to its stdout and stdin.
`ClientSession` wraps those streams in the MCP protocol, and `initialize()`
performs the handshake, where both sides agree on a protocol version before
anything else happens. `list_tools()` asks the server what it offers and gets
back each tool's name, description, and JSON input schema, and `call_tool()`
sends a tool name plus arguments and gets the result back as text content.
The client never imports my code because everything it needs to know arrives
in the `list_tools()` reply. The contract is the protocol, not a Python
import. It is `async` because every step is waiting on another process to
reply over a pipe, and `await` lets the program pause there without blocking.

## Part 3: Writeup

### Why MCP over hardcoded functions

1. **I could test the tool logic without any MCP at all.** Because the real
   logic lives in `external_tool.py` as a plain function and `mcp_server.py`
   only wraps it, I debugged my error handling by running
   `uv run python external_tool.py` directly, with no server or client
   involved. In HW1 my tools were wired straight into the agent's dispatcher,
   so testing one meant running the whole agent loop.
2. **The client discovers the tools at runtime.** `mcp_client.py` never
   imports `mcp_server.py` or hardcodes my function names. When I renamed an
   argument while testing, the model saw the new schema on the next run with
   no change to the client. The same server could sit behind Claude Desktop or
   a different agent framework unchanged. With in-process functions, every
   consumer has to import my module and match my signatures exactly.

### A tool schema

```python
@mcp.tool()
def retrieve(query: str) -> str:
    """Semantic (embedding) search over the same local corpus. Use when the
    question is about an idea or uses different wording than the documents
    might, e.g. "how does an agent decide what to do next". Pass the full
    question. Returns the 3 most similar passages."""
    return "\n\n".join(_retrieve(query, k=3))
```

What makes this good is that it does not just restate the function name. It
tells the model **when** to prefer this tool **over `search`, which covers the
same documents**. "Same local corpus" signals that the two overlap, and
"different wording than the documents" is the actual deciding rule. It also
says what to pass (the full question, because embeddings work best on
complete sentences) and what comes back. The `query: str` hint matters too:
FastMCP turns it into `{"type": "string"}`, so the model knows to send a plain
string.

**What breaks with a vague description.** When I temporarily changed this
docstring to "Retrieve stuff.", the model sent the paraphrased agent question
to `search`, which matched only on "agent" and missed the ReAct sentence.
Nothing crashed. The answer was just quietly worse. That is the real danger:
a vague description doesn't cause an error, it causes silently wrong tool
selection, which is much harder to notice than an exception.
