"""Sensor platform for Ookla Speedtest integration."""

import logging
import subprocess
import json
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_SERVER_ID,
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    SERVICE_RUN_SPEEDTEST,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    try:
        server_id = entry.data.get(CONF_SERVER_ID, "closest")
        manual = entry.data.get(CONF_MANUAL, True)
        scan_interval = entry.data.get(CONF_SCAN_INTERVAL, 30)

        # Validate server_id during setup
        if server_id != "closest" and (not server_id or not server_id.isdigit()):
            _LOGGER.warning(f"Invalid server_id '{server_id}' in config entry; defaulting to 'closest'")
            server_id = "closest"

        _LOGGER.debug(f"Setting up integration with server_id: {server_id}, manual: {manual}, scan_interval: {scan_interval}")

        # Create a coordinator to manage speed test updates
        coordinator = SpeedtestCoordinator(hass, entry, server_id, scan_interval, manual)

        # Create sensors
        sensors = [
            OoklaSpeedtestSensor(coordinator, entry, "ping", "Ping", "ms"),
            OoklaSpeedtestSensor(coordinator, entry, "download", "Download", "Mbit/s"),
            OoklaSpeedtestSensor(coordinator, entry, "upload", "Upload", "Mbit/s"),
            OoklaSpeedtestSensor(coordinator, entry, "jitter", "Jitter", "ms"),
            OoklaSpeedtestSensor(coordinator, entry, "server", "Server", None),
            OoklaSpeedtestSensor(coordinator, entry, "isp", "ISP", None),
        ]

        async_add_entities(sensors, update_before_add=not manual)
        _LOGGER.debug("Sensors added successfully")

        # Register service to manually run a speed test
        async def run_speedtest_service(call) -> None:
            """Service to manually run a speedtest."""
            try:
                if coordinator is None:
                    _LOGGER.error("Coordinator not initialized for run_speedtest service")
                    raise HomeAssistantError("Speedtest coordinator not initialized")
                await coordinator.async_request_refresh()
                _LOGGER.debug("Speedtest service triggered successfully")
            except Exception as e:
                _LOGGER.error(f"Failed to run speedtest service: {e}")
                raise HomeAssistantError(f"Failed to run speedtest: {e}")

        hass.services.async_register(DOMAIN, SERVICE_RUN_SPEEDTEST, run_speedtest_service)
        _LOGGER.debug("Speedtest service registered successfully")

        # Trigger initial update if not manual
        if not manual:
            await coordinator.async_config_entry_first_refresh()
            _LOGGER.debug("Initial refresh triggered for automatic mode")

    except Exception as e:
        _LOGGER.error(f"Failed to set up Ookla Speedtest integration: {e}")
        raise HomeAssistantError(f"Setup failed for Ookla Speedtest: {e}")

class SpeedtestCoordinator(DataUpdateCoordinator):
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
        _LOGGER.debug(f"Coordinator initialized with server_id: {self.server_id}")

    async def _async_update_data(self):
        """Fetch new data from speedtest-cli."""
        try:
            cmd = ["/config/shell/launch_speedtest.sh"]
            if self.server_id != "closest" and self.server_id and self.server_id.isdigit():
                cmd.append(f"-s {self.server_id}")
                _LOGGER.debug(f"Running speedtest command: {' '.join(cmd)} with server_id: {self.server_id}")
            else:
                _LOGGER.debug(f"Running speedtest command: {' '.join(cmd)} without server_id (using closest server): {self.server_id}")
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
            )
            result = json.loads(process.stdout)
            _LOGGER.debug("Speedtest completed successfully")
            return {
                "ping": round(result["ping"]["latency"], 2),
                "download": round(result["download"]["bandwidth"] * 8 / 1000000, 2),
                "upload": round(result["upload"]["bandwidth"] * 8 / 1000000, 2),
                "jitter": round(result["ping"]["jitter"], 2),
                "server": f"{result['server']['name']} ({result['server']['location']}, {result['server']['country']})",
                "isp": result["isp"],
            }
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Speedtest failed: {e.stderr}. Command: {' '.join(cmd)}")
            return None
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Failed to parse Speedtest JSON output: {e}. Output: {process.stdout}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error during speedtest: {e}. Command: {' '.join(cmd)}")
            return None

class OoklaSpeedtestSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Speedtest sensor."""

    def __init__(
        self,
        coordinator: SpeedtestCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        unit: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_name = f"Speedtest {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_unit_of_measurement = unit
        _LOGGER.debug(f"Sensor initialized: {self._attr_name}")

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)
