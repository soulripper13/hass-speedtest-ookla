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
    """Coordinator for Speedtest.net data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, binary_path: str) -> None:
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
        try:
            # Version detection
            proc = await asyncio.create_subprocess_exec(
                self._binary_path,
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            version_text = stdout.decode("utf-8", errors="ignore").strip()
            current_version = version_text.replace("Speedtest by Ookla", "").strip()

            # Fetch latest version
            session = async_get_clientsession(self.hass)
            async with session.get("https://packagecloud.io/ookla/speedtest-cli/") as resp:
                html = await resp.text()
                match = re.search(r"(\d+\.\d+\.\d+\.\d+-\d+)", html)
                latest_version = match.group(1) if match else "unknown"

            # Run speedtest with JSON
            proc = await asyncio.create_subprocess_exec(
                self._binary_path,
                "--accept-license",
                "--accept-gdpr",
                "--format=json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            output = stdout.decode("utf-8", errors="ignore").strip()
            err = stderr.decode("utf-8", errors="ignore").strip()

            # Detect invalid (help menu)
            if "Usage:" in output or "Valid output formats" in output:
                _LOGGER.error("Speedtest CLI does not support JSON output. Installed version is outdated: %s", output)
                raise UpdateFailed("Outdated Speedtest CLI - install latest binary from speedtest.net")

            data = _parse_output(output)
            data[ATTR_CURRENT_VERSION] = current_version
            data[ATTR_LATEST_VERSION] = latest_version

            return data

        except Exception as err:
            raise UpdateFailed(f"Failed to update Speedtest: {err}") from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    binary_path = hass.data[DOMAIN][entry.entry_id]["binary_path"]
    coordinator = SpeedtestSensorData(hass, entry, binary_path)

    try:
        await coordinator.async_config_entry_first_refresh()
    except UpdateFailed:
        raise ConfigEntryNotReady("Speedtest CLI initial run failed")

    hass.data[DOMAIN][entry.entry_id]["coordinator"] = coordinator

    entities = [SpeedtestSensor(coordinator, desc) for desc in SENSORS]
    async_add_entities(entities)


class SpeedtestSensor(CoordinatorEntity, SensorEntity):
    """Single sensor entity for Speedtest."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, coordinator, description):
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def native_value(self):
        val = self.coordinator.data.get(self.entity_description.key)
        if isinstance(val, (int, float)):
            return round(float(val), 2)
        return val

    @property
    def extra_state_attributes(self):
        return {
            k: v for k, v in self.coordinator.data.items()
            if k != self.entity_description.key
        }


def _parse_output(output: str) -> dict[str, Any]:
    """Parse Ookla Speedtest JSON output safely."""
    try:
        json_data = json.loads(output)
    except json.JSONDecodeError:
        _LOGGER.error("Failed to parse Speedtest.net CLI output: %s", output)
        raise UpdateFailed("Invalid JSON output (CLI likely outdated)")

    download = json_data.get("download", {}).get("bandwidth", 0) * 8 / 1_000_000
    upload = json_data.get("upload", {}).get("bandwidth", 0) * 8 / 1_000_000

    return {
        ATTR_DOWNLOAD: download,
        ATTR_UPLOAD: upload,
        ATTR_PING: json_data.get("ping", {}).get("latency"),
        ATTR_JITTER: json_data.get("ping", {}).get("jitter"),
        ATTR_ISP: json_data.get("isp"),
        ATTR_SERVER: json_data.get("server", {}).get("name"),
    }
