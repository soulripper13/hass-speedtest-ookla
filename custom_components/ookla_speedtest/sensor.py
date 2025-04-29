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
    server_id = entry.data.get(CONF_SERVER_ID, "closest")
    manual = entry.data[CONF_MANUAL]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    # Create a coordinator to manage speed test updates
    coordinator = SpeedtestCoordinator(hass, entry, server_id, scan_interval, manual)

    # Create sensors
    sensors = [
        OoklaSpeedtestSensor(coordinator, entry, "ping", "Ping", "ms"),
        OoklaSpeedtestSensor(coordinator, entry, "download", "Download", "Mbit/s"),
        OoklaSpeedtestSensor(coordinator, entry, "upload", "Upload", "Mbit/s"),
    ]

    async_add_entities(sensors, update_before_add=not manual)

    # Register service to manually run a speed test
    async def run_speedtest_service(call) -> None:
        """Service to manually run a speedtest."""
        await coordinator.async_request_refresh()

    hass.services.async_register(DOMAIN, SERVICE_RUN_SPEEDTEST, run_speedtest_service)

    # Trigger initial update if not manual
    if not manual:
        await coordinator.async_config_entry_first_refresh()


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

    async def _async_update_data(self):
        """Fetch new data from speedtest-cli."""
        try:
            cmd = ["/config/shell/launch_speedtest.sh"]
            if self.server_id != "closest":
                cmd.append(f"-s {self.server_id}")
            _LOGGER.debug(f"Running speedtest command: {' '.join(cmd)}")
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
            )
            result = json.loads(process.stdout)
            _LOGGER.debug("Speedtest completed successfully")
            return {
                "ping": round(result["ping"]["latency"], 2),
                "download": round(
                    result["download"]["bandwidth"] * 8 / 1000000, 2
                ),  # Convert bytes/s to Mbit/s
                "upload": round(
                    result["upload"]["bandwidth"] * 8 / 1000000, 2
                ),  # Convert bytes/s to Mbit/s
            }
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Speedtest failed: {e.stderr}")
            return None
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Failed to parse Speedtest JSON output: {e}")
            return None
        except Exception as e:
            _LOGGER.error(f"Unexpected error during speedtest: {e}")
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

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)
