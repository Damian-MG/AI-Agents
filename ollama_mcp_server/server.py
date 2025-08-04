import argparse
import sqlite3
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP('sqlite-damian')


def init_db():
    conn = sqlite3.connect('demo.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            profession TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor


@mcp.tool()
def add_data(query: str) -> bool:
    """
    Add new data to the people table using a SQL INSERT query.

    Args:
        query (str): SQL INSERT query following this format:
            INSERT INTO people (name, age, profession)
            VALUES ('John Doe', 30, 'Engineer')
        
    Schema:
        - name: Text field (required)
        - age: Integer field (required)
        - profession: Text field (required)
        Note: 'id' field is auto-generated
    
    Returns:
        bool: True if data was added successfully, False otherwise
    
    Example:
        >>> query = '''
        ... INSERT INTO people (name, age, profession)
        ... VALUES ('Alice Smith', 25, 'Developer')
        ... '''
        >>> add_data(query)
        True
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding data: {e}")
        return False
    finally:
        conn.close()


@mcp.tool()
def read_data(query: str = "SELECT * FROM people") -> list:
    """
    Read data from the people table using a SQL SELECT query.

    Args:
        query (str, optional): SQL SELECT query. Defaults to "SELECT * FROM people".
            Examples:
            - "SELECT * FROM people"
            - "SELECT name, age FROM people WHERE age > 25"
            - "SELECT * FROM people ORDER BY age DESC"
    
    Returns:
        list: List of tuples containing the query results.
              For default query, tuple format is (id, name, age, profession)
    
    Example:
        >>> # Read all records
        >>> read_data()
        [(1, 'John Doe', 30, 'Engineer'), (2, 'Alice Smith', 25, 'Developer')]
        
        >>> # Read with custom query
        >>> read_data("SELECT name, profession FROM people WHERE age < 30")
        [('Alice Smith', 'Developer')]
    """
    conn, cursor = init_db()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        conn.close()


@mcp.tool()
def get_weather(city_name) -> str:
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
    
    Example:
        >>> # Get the weather in Madrid
        >>> get_weather("Madrid")  
    """
    geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_params = {"name": city_name, "count": 1, "language": "en", "format": "json"}

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


if __name__ == "__main__":
    # Start the server
    print("🚀Starting server... ")

    # Debug Mode
    #  uv run mcp dev server.py

    # Production Mode
    # uv run server.py --server_type=sse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"]
    )

    args = parser.parse_args()
    mcp.run(args.server_type)
