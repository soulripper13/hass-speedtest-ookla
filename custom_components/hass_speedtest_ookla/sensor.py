"""Support for Speedtest.net sensors."""
from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_AUTO_UPDATE,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    ATTR_DOWNLOAD,
    ATTR_UPLOAD,
    ATTR_PING,
    ATTR_JITTER,
    ATTR_ISP,
    ATTR_SERVER,
    ATTR_CURRENT_VERSION,
    ATTR_LATEST_VERSION,
)

_LOGGER = logging.getLogger(__name__)

SENSORS = (
    SensorEntityDescription(
        key=ATTR_DOWNLOAD,
        name="Download",
        native_unit_of_measurement="Mbit/s",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_UPLOAD,
        name="Upload",
        native_unit_of_measurement="Mbit/s",
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_PING,
        name="Ping",
        native_unit_of_measurement="ms",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_JITTER,
        name="Jitter",
        native_unit_of_measurement="ms",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_ISP,
        name="ISP",
        icon="mdi:server-network",
    ),
    SensorEntityDescription(
        key=ATTR_SERVER,
        name="Server",
        icon="mdi:server",
    ),
    SensorEntityDescription(
        key=ATTR_CURRENT_VERSION,
        name="Current Version",
        icon="mdi:package-variant-closed",
    ),
    SensorEntityDescription(
        key=ATTR_LATEST_VERSION,
        name="Latest Version",
        icon="mdi:package-variant",
    ),
)


class SpeedtestSensorData(DataUpdateCoordinator):
    """Data for Speedtest.net sensors."""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, binary_path: str
    ) -> None:
        """Initialize the coordinator."""
        self._binary_path = binary_path
        self.entry = entry

        options = entry.options
        auto_update = options.get(CONF_AUTO_UPDATE, True)
        interval = timedelta(
            seconds=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        ) if auto_update else None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=interval,
            update_method=self._async_update_data,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Speedtest CLI binary."""
        try:
            # Get current version
            proc = await asyncio.create_subprocess_exec(
                self._binary_path,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            version_output = stdout.decode("utf-8", errors="ignore").strip()
            current_version = version_output.split(" ")[1]

            # Get latest version
            session = async_get_clientsession(self.hass)
            async with session.get("https://packagecloud.io/ookla/speedtest-cli/") as resp:
                if resp.status == 200:
                    html = await resp.text()
                    match = re.search(r"(\d+\.\d+\.\d+\.\d+-\d+)", html)
                    latest_version = match.group(1) if match else "unknown"
                else:
                    latest_version = "unknown"

            # Run speedtest
            proc = await asyncio.create_subprocess_exec(
                self._binary_path,
                "--accept-license",
                "--accept-gdpr",
                "--json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode("utf-8", errors="ignore")

            _LOGGER.debug("Speedtest CLI Raw Output: %s", output)
            if stderr:
                _LOGGER.debug("Speedtest CLI Stderr: %s", stderr.decode("utf-8", errors="ignore"))

            data = _parse_output(output, SENSORS)
            data[ATTR_CURRENT_VERSION] = current_version
            data[ATTR_LATEST_VERSION] = latest_version
            return data

        except Exception as err:
            _LOGGER.error("Error running Speedtest.net CLI binary: %s", err)
            raise UpdateFailed(f"Failed to update: {err}")


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Speedtest.net sensors."""
    hass_data = hass.data[DOMAIN][entry.entry_id]
    binary_path = hass_data["binary_path"]

    coordinator = SpeedtestSensorData(hass, entry, binary_path)

    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed:
        raise ConfigEntryNotReady("Speedtest.net initial run failed")

    hass_data["coordinator"] = coordinator

    sensors = [
        SpeedtestSensor(coordinator, description)
        for description in SENSORS
    ]
    async_add_entities(sensors)


class SpeedtestSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Speedtest.net sensor."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        coordinator: SpeedtestSensorData,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}.{description.key}"

    @property
    def native_value(self) -> StateType | str | None:
        raw_value = self.coordinator.data.get(self.entity_description.key)
        if raw_value is None or raw_value == "unknown":
            if self.entity_description.native_unit_of_measurement:
                return None
            return "unknown"

        try:
            parsed = float(raw_value)
            return round(parsed, 2)
        except ValueError:
            return raw_value

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            key: self.coordinator.data.get(key, "unknown")
            for key in self.coordinator.data
            if key != self.entity_description.key
        }


# ---------------------------------------------------------------------------
# NEW ROBUST JSON PARSER (handles all new Ookla formats)
# ---------------------------------------------------------------------------

def _parse_output(output: str, sensors: tuple[SensorEntityDescription, ...]) -> dict[str, str]:
    """Parse Speedtest CLI output. Compatible with all new Ookla JSON formats."""
    data = {desc.key: "unknown" for desc in sensors}

    # Extract valid JSON even if warnings or logs exist
    try:
        start = output.find("{")
        end = output.rfind("}") + 1
        if start == -1 or end == -1:
            raise ValueError
        clean_json = output[start:end]
        json_output = json.loads(clean_json)
    except Exception:
        _LOGGER.error("Failed to parse Speedtest.net CLI output: %s", output)
        return data

    # DOWNLOAD
    dl = json_output.get("download", {})
    if "bandwidth" in dl:
        data[ATTR_DOWNLOAD] = dl["bandwidth"] * 8 / 1_000_000
    elif "bytes" in dl and "elapsed" in dl:
        seconds = max(dl["elapsed"] / 1000, 0.001)
        data[ATTR_DOWNLOAD] = (dl["bytes"] * 8) / seconds / 1_000_000

    # UPLOAD
    ul = json_output.get("upload", {})
    if "bandwidth" in ul:
        data[ATTR_UPLOAD] = ul["bandwidth"] * 8 / 1_000_000
    elif "bytes" in ul and "elapsed" in ul:
        seconds = max(ul["elapsed"] / 1000, 0.001)
        data[ATTR_UPLOAD] = (ul["bytes"] * 8) / seconds / 1_000_000

    # PING/JITTER
    ping = json_output.get("ping", {})
    data[ATTR_PING] = ping.get("latency", "unknown")
    data[ATTR_JITTER] = ping.get("jitter", "unknown")

    # ISP
    data[ATTR_ISP] = json_output.get("isp", "unknown")

    # SERVER NAME
    server = json_output.get("server", {})
    data[ATTR_SERVER] = server.get("name", "unknown")

    return data
