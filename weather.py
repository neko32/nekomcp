from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
from loguru import logger

# Initialize FastMCP server
mcp = FastMCP("weather")

# Constants
API_BASE = "https://api.weather.gov"
NEKO_USER_AGENT = "nekomcp_srv_weather"

async def make_nws_request(url: str) -> dict[str, Any] | None:
    """Make a request to the NWS API with proper error handling."""
    headers = {
        "User-Agent": NEKO_USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

def format_alert(feature: dict) -> str:
    """Format an alert feature into a readable string."""
    props = feature["properties"]
    return f"""
Event: {props.get('event', 'Unknown')}
Area: {props.get('areaDesc', 'Unknown')}
Severity: {props.get('severity', 'Unknown')}
Description: {props.get('description', 'No description available')}
Instructions: {props.get('instruction', 'No specific instructions provided')}
"""


@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state.

    Args:
        state: Two-letter US state code (e.g. CA, NY)
    """
    url = f"{API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."

    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    point_req_url = f"{API_BASE}/points/{latitude},{longitude}"
    logger.info(f"making a request to {point_req_url} ... ")
    points_resp = await make_nws_request(point_req_url)
    logger.info(f"received a response for point.")
    print(points_resp)

    if not points_resp:
        return "Unable to fetch forecast data for this location."

    # Get the forecast URL from the points response
    forecast_url = points_resp["properties"]["forecast"]
    logger.info(f"making a request to {forecast_url}...")
    forecast_resp = await make_nws_request(forecast_url)
    logger.info("received a response for forecast.")
    logger.info(forecast_resp)

    if not forecast_resp:
        return "Unable to fetch detailed forecast."

    # Format the periods into a readable forecast
    periods = forecast_resp["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
{period['name']}:
Temperature: {period['temperature']}°{period['temperatureUnit']}
Wind: {period['windSpeed']} {period['windDirection']}
Forecast: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)



if __name__ == "__main__":
    # Initialize and run the server
    print("initializing logger..")
    logger.remove()
    logger.add("/var/nekokan_log/nekomcp/weather/weather.log")
    logger.info("starting MCP Server 'Weather'...")
    mcp.run(transport='stdio')

