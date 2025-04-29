import logging
import subprocess
import json
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN, CONF_SERVER_ID, CONF_MANUAL, CONF_SCAN_INTERVAL, SERVICE_RUN_SPEEDTEST

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform."""
    server_id = entry.data.get(CONF_SERVER_ID, "closest")
    manual = entry.data[CONF_MANUAL]
    scan_interval = entry.data[CONF_SCAN_INTERVAL]

    sensors = [
        OoklaSpeedtestSensor(hass, entry, "ping", "Ping", "ms"),
        OoklaSpeedtestSensor(hass, entry, "download", "Download", "Mbit/s"),
        OoklaSpeedtestSensor(hass, entry, "upload", "Upload", "Mbit/s"),
    ]

    async_add_entities(sensors, update_before_add=not manual)

    if not manual:
        for sensor in sensors:
            sensor.async_schedule_update_ha_state(True)

    async def run_speedtest_service(call):
        """Service to manually run a speedtest."""
        for sensor in sensors:
            await sensor.async_update()

    hass.services.async_register(DOMAIN, SERVICE_RUN_SPEEDTEST, run_speedtest_service)

class OoklaSpeedtestSensor(SensorEntity):
    """Representation of a Speedtest sensor."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, key: str, name: str, unit: str):
        """Initialize the sensor."""
        self._hass = hass
        self._entry = entry
        self._key = key
        self._attr_name = f"Speedtest {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_unit_of_measurement = unit
        self._state = None
        self._server_id = entry.data.get(CONF_SERVER_ID, "closest")

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            cmd = ["/config/shell/launch_speedtest.sh"]
            if self._server_id != "closest":
                cmd.append(f"-s {self._server_id}")
            process = await self._hass.async_add_executor_job(
                lambda: subprocess.run(cmd, capture_output=True, text=True, check=True)
            )
            result = json.loads(process.stdout)
            if self._key == "ping":
                self._state = round(result["ping"]["latency"], 2)
            elif self._key == "download":
                self._state = round(result["download"]["bandwidth"] * 8 / 1000000, 2)  # Convert bytes/s to Mbit/s
            elif self._key == "upload":
                self._state = round(result["upload"]["bandwidth"] * 8 / 1000000, 2)  # Convert bytes/s to Mbit/s
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Speedtest failed: {e.stderr}")
            self._state = None
        except json.JSONDecodeError:
            _LOGGER.error("Failed to parse Speedtest JSON output")
            self._state = None
