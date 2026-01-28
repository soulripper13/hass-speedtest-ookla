"""Helper functions for Ookla Speedtest integration."""

import json
import logging
import subprocess
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant

from .const import SPEEDTEST_BIN_PATH

_LOGGER = logging.getLogger(__name__)


def validate_time_format(time_str: str | None) -> bool:
    """Validate time string format (HH:MM or HH:MM:SS).

    Args:
        time_str: The time string to validate

    Returns:
        True if valid or empty, False otherwise
    """
    if not time_str:
        return True
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            datetime.strptime(time_str, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_server_id(server_id: str | None) -> bool:
    """Validate server ID format.

    Args:
        server_id: The server ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not server_id:
        return False
    if server_id == "closest":
        return True
    return server_id.isdigit()


async def get_speedtest_servers(hass: HomeAssistant) -> list[dict[str, Any]]:
    """Fetch the list of 10 closest Speedtest servers.

    Args:
        hass: Home Assistant instance

    Returns:
        List of server dictionaries with id, name, location, and distance
    """
    _LOGGER.debug("Fetching 10 closest Speedtest servers")
    try:
        process = await hass.async_add_executor_job(
            lambda: subprocess.run(
                [
                    SPEEDTEST_BIN_PATH,
                    "--servers",
                    "--format=json",
                    "--accept-license",
                    "--accept-gdpr",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
        )
        servers_data = json.loads(process.stdout)
        servers = servers_data.get("servers", [])

        # Sort by distance and take the 10 closest
        sorted_servers = sorted(
            servers, key=lambda x: x.get("distance", float("inf"))
        )
        result = []
        for server in sorted_servers[:10]:
            # Safely access server data with fallbacks
            city = server.get("city", server.get("location", "Unknown City"))
            country = server.get("country", server.get("region", "Unknown Country"))
            name = server.get("name", "Unknown Server")
            distance = round(server.get("distance", 0), 2)
            server_id = str(server.get("id", ""))

            if not server_id:
                _LOGGER.warning("Skipping server with missing ID: %s", name)
                continue

            result.append(
                {
                    "id": server_id,
                    "name": name,
                    "location": f"{city}, {country}",
                    "distance": distance,
                }
            )
        _LOGGER.debug("Retrieved %d valid servers", len(result))
        return result
    except subprocess.CalledProcessError as e:
        _LOGGER.error("Failed to fetch server list: %s", e.stderr)
        return []
    except json.JSONDecodeError as e:
        _LOGGER.error("Failed to parse server list JSON: %s", e)
        return []
    except Exception as e:
        _LOGGER.error("Unexpected error fetching servers: %s", str(e))
        return []
