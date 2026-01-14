"""Initialize the Ookla Speedtest integration."""

import json
import logging
import os
import stat
import subprocess
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    ATTR_DOWNLOAD,
    ATTR_DOWNLOAD_LATENCY_IQM,
    ATTR_DOWNLOAD_LATENCY_LOW,
    ATTR_DOWNLOAD_LATENCY_HIGH,
    ATTR_DOWNLOAD_LATENCY_JITTER,
    ATTR_ISP,
    ATTR_JITTER,
    ATTR_PING,
    ATTR_PING_LOW,
    ATTR_PING_HIGH,
    ATTR_RESULT_URL,
    ATTR_SERVER,
    ATTR_UPLOAD,
    ATTR_UPLOAD_LATENCY_IQM,
    ATTR_UPLOAD_LATENCY_LOW,
    ATTR_UPLOAD_LATENCY_HIGH,
    ATTR_UPLOAD_LATENCY_JITTER,
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    CONF_SERVER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    INTEGRATION_SHELL_DIR,
    LAUNCH_SCRIPT_PATH,
    SERVICE_RUN_SPEEDTEST,
    STARTUP_DELAY,
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

            _LOGGER.debug("Result from speedtest invocation: %s", result)

            return {
                # ping { jitter, latency, low, high}
                ATTR_PING: round(result["ping"]["latency"], 2),
                ATTR_JITTER: round(result["ping"]["jitter"], 2),
                ATTR_PING_LOW: round(result["ping"]["low"], 2),
                ATTR_PING_HIGH: round(result["ping"]["high"], 2),
                # download { bandwidth, bytes, elapsed, latency { iqm, low, high, jitter }}
                ATTR_DOWNLOAD: round(result["download"]["bandwidth"] * 8 / 1000000, 2),
                ATTR_DOWNLOAD_LATENCY_IQM: round(result["download"]["latency"]["iqm"], 2),
                ATTR_DOWNLOAD_LATENCY_LOW: round(result["download"]["latency"]["low"], 2),
                ATTR_DOWNLOAD_LATENCY_HIGH: round(result["download"]["latency"]["high"], 2),
                ATTR_DOWNLOAD_LATENCY_JITTER: round(result["download"]["latency"]["jitter"], 2),
                # upload { bandwidth, bytes, elapsed, latency { iqm, low, high, jitter }}
                ATTR_UPLOAD: round(result["upload"]["bandwidth"] * 8 / 1000000, 2),
                ATTR_UPLOAD_LATENCY_IQM: round(result["upload"]["latency"]["iqm"], 2),
                ATTR_UPLOAD_LATENCY_LOW: round(result["upload"]["latency"]["low"], 2),
                ATTR_UPLOAD_LATENCY_HIGH: round(result["upload"]["latency"]["high"], 2),
                ATTR_UPLOAD_LATENCY_JITTER: round(result["upload"]["latency"]["jitter"], 2),
                # isp
                ATTR_ISP: result["isp"],
                # interface { internalIp, name, macAddr, isVpn, externalIp }
                # server { id, host, port, name, location, country, ip }
                ATTR_SERVER: (
                    # produces: Boost Mobile (Chicago, IL, United States)
                    f"{result['server']['name']} "
                    f"({result['server']['location']}, {result['server']['country']})"
                ),
                # result { id, url, persisted }
                ATTR_RESULT_URL: result.get("result", {}).get("url", ""),
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

    # Delay first speedtest in interval mode to avoid blocking HA startup
    if not manual:
        async def schedule_first_refresh(_):
            """Schedule the first speedtest after HA has started."""
            # Wait for configured delay after HA startup before running first test
            async def run_first_refresh(_):
                await coordinator.async_request_refresh()

            async_call_later(hass, STARTUP_DELAY, run_first_refresh)

        # If HA is already started, schedule immediately; otherwise wait for start event
        if hass.is_running:
            await schedule_first_refresh(None)
        else:
            hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, schedule_first_refresh)

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
