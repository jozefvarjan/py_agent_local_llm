from datetime import datetime
import ast
from pathlib import Path

from langchain_core.tools import tool

@tool
def current_time() -> str:
    """Return the current local date and time.
    Use this when the user asks what time or date it is.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def word_count(text: str) -> int:
    """Count the number of words in a piece of text.
    Use this when the user asks how long a piece of writing is,
    or asks you to count the words in something they've shared.
    Returns the word count as an integer.
    """
    return len(text.split())

@tool
def letter_count(text: str) -> dict[str, int]:
    """Count the number of letters in a piece of text.
    Use this when user asks how many time each letter in
    text is occurred.
    Returns the letter count as dict {<letter>: <count of letter>, ...}
    """
    letter_map = {k:0 for k in set(text)}
    for l in text:
         letter_map[l] += 1
    return letter_map


def discover_tools():
    """Read this file, find every function decorated with @tool, and return
    the list of tool objects.

    Parses the source with `ast` so we don't have to import anything, then
    resolves each discovered name to the actual (decorated) object living in
    this module's namespace.
    """
    source = Path(__file__).read_text()
    tree = ast.parse(source)

    names = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            # Handles both `@tool` and `@tool(...)`.
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if isinstance(target, ast.Name) and target.id == "tool":
                names.append(node.name)
                break

    return [globals()[name] for name in names]


TOOLS = discover_tools()
