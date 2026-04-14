def get_weather(location: str, **kwargs) -> dict:
    """Mock weather tool."""
    print(f"[Tool: Weather] Fetching weather for {location}...")
    # In a real app we would call something like open-meteo
    return {"temperature": 30, "condition": "Sunny", "location": location}
