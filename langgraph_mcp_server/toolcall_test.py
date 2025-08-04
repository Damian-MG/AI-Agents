import requests
from dotenv import load_dotenv

from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


@tool(description="Get the current weather in a given location.")
def get_weather(city_name: str) -> str:
    """
    Fetches current weather information for a given city using the Open-Meteo API.
    In order to get the information the longitude and latitude of the city must be provided.

    Args:
        city_name (str): The name of the city to query (e.g., "Madrid").
    
    Returns:
        str: A human-readable string containing:
            - The resolved city name and its coordinates.
            - The current temperature (°C).
            - The current wind speed (km/h).
            - The raw weather code (int).
    """
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city_name,
                  "count": 1,
                  "language": "en",
                  "format": "json"}

    geo_response = requests.get(geocode_url, params=geo_params)
    geo_data = geo_response.json()

    if "results" not in geo_data or len(geo_data["results"]) == 0:
        return f"City '{city_name}' not found."

    location = geo_data["results"][0]
    latitude = location["latitude"]
    longitude = location["longitude"]

    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": True,
    }

    weather_response = requests.get(weather_url, params=weather_params)
    weather_data = weather_response.json()

    if "current_weather" not in weather_data:
        return "Could not fetch current weather data."

    current = weather_data["current_weather"]
    temperature = current["temperature"]
    windspeed = current["windspeed"]
    weather_code = current["weathercode"]

    return (
        f"Weather in {location['name']} ({latitude}, {longitude}):\n"
        f"- Temperature: {temperature}°C\n"
        f"- Wind speed: {windspeed} km/h\n"
        f"- Weather code: {weather_code}"
    )


llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
llm_with_tools = llm.bind_tools([get_weather])

query = "What is the weather in Alicante?"
ai_msg = llm_with_tools.invoke(query)

print(ai_msg.tool_calls)

tool_message = ToolMessage(
    content=get_weather(*ai_msg.tool_calls[0]["args"]),
    tool_call_id=ai_msg.tool_calls[0]["id"],
)
llm_with_tools.invoke([ai_msg, tool_message])
