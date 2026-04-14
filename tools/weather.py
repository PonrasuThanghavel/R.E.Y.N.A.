"""Weather tool implementation.

Provides weather information for specified locations.
"""


def get_weather(location: str, **kwargs) -> dict:
    """Get weather for a location.

    Args:
        location: Location name.
        **kwargs: Additional arguments (unused).

    Returns:
        Dictionary with temperature, condition, and location.
    """
    print(f"[Tool: Weather] Fetching weather for {location}...")
    # In a real app we would call something like open-meteo
    return {"temperature": 30, "condition": "Sunny", "location": location}
