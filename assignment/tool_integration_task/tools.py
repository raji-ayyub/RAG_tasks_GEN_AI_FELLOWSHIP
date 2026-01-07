from langchain_core.tools import tool

@tool
def calculator(expression: str) -> str:
    """
    Evaluate a simple math expression.
    Example: "2 + 3 * 4"
    """
    try:
        return str(eval(expression))
    except Exception:
        return "Invalid math expression"
    

@tool
def search(query: str) -> str:
    """
    Search company knowledge or web-like info.
    """
    knowledge_base = {
        "warranty": "All products have 1-year warranty. Extended 2-year warranty is available.",
        "return": "30-day money-back guarantee on all products.",
        "shipping": "Free shipping on orders over $99."
    }

    for key, value in knowledge_base.items():
        if key in query.lower():
            return value

    return "No relevant information found."
