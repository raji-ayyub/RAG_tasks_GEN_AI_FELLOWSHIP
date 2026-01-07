from langchain_core.tools import tool
import os
from dotenv import load_dotenv
import requests
from duckduckgo_search import DDGS


load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

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
def lookup_dictionary(query: str) -> str:
    """
    lookup dictionary for company knowledge.
    """
    mini_dictionary = {
        "warranty": "All products have 1-year warranty. Extended 2-year warranty is available.",
        "return": "30-day money-back guarantee on all products.",
        "shipping": "Free shipping on orders over $99."
    }

    for key, value in mini_dictionary.items():
        if key in query.lower():
            return value

    return "No relevant information found."



@tool
def search(query: str) -> str:
    """
    Search the web using DuckDuckGo and return top results.
    """
    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(f"- {r['title']}: {r['href']}")

        if not results:
            return "No search results found."

        return "\n".join(results)

    except Exception as e:
        return f"Search error: {str(e)}"


@tool 
def get_weather(city: str) -> dict:
    """
    get weather data for city using this openweathermap tool
    """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code != 200:
        return {"error": data.get("message", "Weather API error")}
    
    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"],
        "humidity": data["main"]["humidity"]
    }