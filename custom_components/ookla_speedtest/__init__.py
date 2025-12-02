"""Initialize the Ookla Speedtest integration."""

import json
import logging
import os
import stat
import subprocess
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    ATTR_DOWNLOAD,
    ATTR_ISP,
    ATTR_JITTER,
    ATTR_PING,
    ATTR_SERVER,
    ATTR_UPLOAD,
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    CONF_SERVER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    INTEGRATION_SHELL_DIR,
    LAUNCH_SCRIPT_PATH,
    SERVICE_RUN_SPEEDTEST,
)
from .helpers import validate_server_id

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


# Set execute permissions on shell scripts
if os.path.isdir(INTEGRATION_SHELL_DIR):
    for script_name in os.listdir(INTEGRATION_SHELL_DIR):
        script_path = os.path.join(INTEGRATION_SHELL_DIR, script_name)
        if script_path.endswith(".sh"):
            try:
                st = os.stat(script_path)
                os.chmod(
                    script_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                )
            except OSError as e:
                _LOGGER.error(
                    "Failed to make shell script %s executable: %s", script_path, e
                )


class SpeedtestCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage Speedtest updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        server_id: str,
        scan_interval: int,
        manual: bool,
    ) -> None:
        """Initialize the coordinator."""
        self.server_id = server_id
        self.entry = entry
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=None if manual else timedelta(minutes=scan_interval),
        )

    async def _async_update_data(self) -> dict[str, Any] | None:
        """Fetch new data from speedtest-cli."""
        cmd = [LAUNCH_SCRIPT_PATH]
        if self.server_id != "closest" and validate_server_id(self.server_id):
            cmd.extend(["-s", self.server_id])

        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
            )
            result = json.loads(process.stdout)

            return {
                ATTR_PING: round(result["ping"]["latency"], 2),
                ATTR_DOWNLOAD: round(result["download"]["bandwidth"] * 8 / 1000000, 2),
                ATTR_UPLOAD: round(result["upload"]["bandwidth"] * 8 / 1000000, 2),
                ATTR_JITTER: round(result["ping"]["jitter"], 2),
                ATTR_SERVER: (
                    f"{result['server']['name']} "
                    f"({result['server']['location']}, {result['server']['country']})"
                ),
                ATTR_ISP: result["isp"],
            }
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Speedtest failed: %s. Command: %s", e.stderr, " ".join(cmd))
            return None
        except json.JSONDecodeError as e:
            _LOGGER.error(
                "Failed to parse Speedtest JSON output: %s. Output: %s",
                e,
                process.stdout if "process" in locals() else "N/A",
            )
            return None
        except (KeyError, TypeError) as e:
            _LOGGER.error("Unexpected data format in speedtest result: %s", e)
            return None
        except Exception as e:
            _LOGGER.error(
                "Unexpected error during speedtest: %s. Command: %s", e, " ".join(cmd)
            )
            return None


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ookla Speedtest from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Get config from options first, fall back to data for backwards compatibility
    server_id = entry.options.get(
        CONF_SERVER_ID, entry.data.get(CONF_SERVER_ID, "closest")
    )
    manual = entry.options.get(CONF_MANUAL, entry.data.get(CONF_MANUAL, True))
    scan_interval = entry.options.get(
        CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    )

    # Validate server_id during setup
    if not validate_server_id(server_id):
        _LOGGER.warning(
            "Invalid server_id '%s' in config entry; defaulting to 'closest'", server_id
        )
        server_id = "closest"

    coordinator = SpeedtestCoordinator(hass, entry, server_id, scan_interval, manual)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register service to manually run a speed test
    async def run_speedtest_service(call: ServiceCall) -> None:
        """Service to manually run a speedtest."""
        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_RUN_SPEEDTEST,
        run_speedtest_service,
    )

    if not manual:
        await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register options update listener
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.services.async_remove(DOMAIN, SERVICE_RUN_SPEEDTEST)
        if entry.entry_id in hass.data[DOMAIN]:
            hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
