"""Sensor platform for Ookla Speedtest integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfDataRate, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import SpeedtestCoordinator
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
    ATTR_SERVER,
    ATTR_UPLOAD,
    ATTR_UPLOAD_LATENCY_IQM,
    ATTR_UPLOAD_LATENCY_LOW,
    ATTR_UPLOAD_LATENCY_HIGH,
    ATTR_UPLOAD_LATENCY_JITTER,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: SpeedtestCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_PING, "Ping", UnitOfTime.MILLISECONDS, "mdi:speedometer"
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_PING_LOW, "Ping Min", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_PING_HIGH, "Ping Max", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_DOWNLOAD_LATENCY_IQM, "Download Ping", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_DOWNLOAD_LATENCY_LOW, "Download Ping Min", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_DOWNLOAD_LATENCY_HIGH, "Download Ping Max", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_UPLOAD_LATENCY_IQM, "Upload Ping", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_UPLOAD_LATENCY_LOW, "Upload Ping Min", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_UPLOAD_LATENCY_HIGH, "Upload Ping Max", UnitOfTime.MILLISECONDS, "mdi:speedometer", enabled_default = False
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_DOWNLOAD,
            "Download",
            UnitOfDataRate.MEGABITS_PER_SECOND,
            "mdi:download",
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UPLOAD,
            "Upload",
            UnitOfDataRate.MEGABITS_PER_SECOND,
            "mdi:upload",
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_JITTER,
            "Jitter",
            UnitOfTime.MILLISECONDS,
            "mdi:pulse",
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_DOWNLOAD_LATENCY_JITTER,
            "Download Jitter",
            UnitOfTime.MILLISECONDS,
            "mdi:pulse",
            enabled_default = False,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UPLOAD_LATENCY_JITTER,
            "Upload Jitter",
            UnitOfTime.MILLISECONDS,
            "mdi:pulse",
            enabled_default = False,
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_SERVER, "Server", None, "mdi:server"
        ),
        OoklaSpeedtestSensor(coordinator, entry, ATTR_ISP, "ISP", None, "mdi:web"),
    ]

    # Don't update before adding to avoid blocking HA startup
    async_add_entities(sensors, update_before_add=False)


class OoklaSpeedtestSensor(CoordinatorEntity[SpeedtestCoordinator], SensorEntity):
    """Representation of a Speedtest sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SpeedtestCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        unit: str | None,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon

        # Set state class for numeric sensors to enable statistics
        if key in (ATTR_PING, ATTR_DOWNLOAD, ATTR_UPLOAD, ATTR_JITTER):
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name="Ookla Speedtest",
            manufacturer="Ookla",
            model="Speedtest CLI",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)
