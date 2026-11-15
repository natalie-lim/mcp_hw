"""
external_tool.py - Part 1: a real external API (Wikipedia) as a tool.

Your agent's corpus only knows about five short local documents. This tool
lets it answer general-knowledge questions by asking Wikipedia instead.

The file has two functions:

    fetch_summary(title) -> dict       PROVIDED. Does all the networking.
    wikipedia_summary(title) -> str    TODO. Turns that dict into clean text.

You do not need to know anything about HTTP or web scraping. `fetch_summary`
already sends the request, waits for the reply, parses the JSON, and catches
every network error. Your job is only to read fields out of the dictionary it
returns and build the string the model will see.

Try it at any time with:

    uv run python external_tool.py
"""
from __future__ import annotations
import json
import urllib.error
import urllib.parse
import urllib.request

API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
# Wikipedia asks every program that uses its API to identify itself. Requests
# without a User-Agent header can be rejected with HTTP 403.
USER_AGENT = "cis1990-hw3/1.0 (course assignment)"
TIMEOUT_SECONDS = 10


def fetch_summary(title: str) -> dict:
    """fetch_summary - PROVIDED. Download one Wikipedia page summary.

    Parameters:
        title (str): An article title, such as "Alan Turing".

    Returns:
        dict: On success, the JSON dictionary Wikipedia sent back. On failure,
        a dictionary with one key, "error":

            {"error": "not_found"}          the page does not exist (HTTP 404)
            {"error": "<other message>"}    any other problem (timeout, no
                                            internet, server error, bad JSON)

    Description:
        This function never raises. A successful reply looks like this
        (trimmed to the fields you need):

            {
              "type": "standard",
              "title": "Alan Turing",
              "description": "English computer scientist (1912-1954)",
              "extract": "Alan Mathison Turing was an English mathematician...",
              "content_urls": {
                "desktop": {"page": "https://en.wikipedia.org/wiki/Alan_Turing"}
              }
            }

        Not every page has every field. "description" and "content_urls" can
        be missing, and "type" is "disambiguation" when the title could mean
        several different pages (for example "Mercury").
    """
    # Wikipedia page URLs use underscores for spaces. quote() escapes any
    # other characters (like "/" or accented letters) so the URL stays valid.
    url = API + urllib.parse.quote(title.strip().replace(" ", "_"), safe="")
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        # The server answered, but with an error status code.
        if error.code == 404:
            return {"error": "not_found"}
        return {"error": f"HTTP {error.code}"}
    except Exception as error:
        # No answer at all (timeout, no internet) or an unreadable answer.
        # A tool should report problems as text, never crash the agent.
        return {"error": str(error) or type(error).__name__}


def wikipedia_summary(title: str) -> str:
    """wikipedia_summary - TODO. Return a clean, readable Wikipedia summary.

    Parameters:
        title (str): An article title, such as "Alan Turing".

    Returns:
        str: Always a string, never an exception. See README.md, Part 1, for
        the exact format of each case:

        1. Blank title          -> a message asking for a title. Do not call
                                   fetch_summary at all.
        2. "error" in the data  -> a "not found" message for "not_found", or a
                                   "could not reach Wikipedia" message for any
                                   other error. Include the title either way.
        3. Disambiguation page  -> a message that includes the title and the
                                   word "ambiguous".
        4. No "extract" text    -> a "no summary available" message with the
                                   title.
        5. Success              -> three lines:
                                       Title - description
                                       extract
                                       Source: url
                                   Leave out " - description" when there is no
                                   description, and leave out the Source line
                                   when there is no URL.

    Hints:
        - Use data.get("key") instead of data["key"]. It returns None instead
          of raising KeyError when a field is missing.
        - The URL is nested two levels deep. Chained .get() calls with a {}
          default reach it safely:
              data.get("content_urls", {}).get("desktop", {}).get("page")
        - Build the result as a list of lines and finish with "\\n".join(lines).
    """
    # TODO 1: if title is empty or only whitespace, return a message asking
    #         for a title (and do not call fetch_summary).

    # TODO 2: call fetch_summary(title) and store the dictionary.

    # TODO 3: if the dictionary has an "error" key, return the matching
    #         "not found" or "could not reach Wikipedia" message.

    # TODO 4: if data.get("type") is "disambiguation", return a message that
    #         says the title is ambiguous.

    # TODO 5: read "extract". If it is missing or empty, return a
    #         "no summary available" message.

    # TODO 6: read "title", "description", and the nested page URL, then
    #         build and return the three-line summary.
    raise NotImplementedError


if __name__ == "__main__":
    # One real page, one page that does not exist, and one ambiguous title.
    # Paste this output into writeup.md for Part 1.
    for example in ["Alan Turing", "Definitely Not A Real Page 12345", "Mercury"]:
        print(f">>> wikipedia_summary({example!r})")
        print(wikipedia_summary(example))
        print()
