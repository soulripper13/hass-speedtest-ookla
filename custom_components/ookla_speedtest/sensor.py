"""Sensor platform for Ookla Speedtest integration."""

<<<<<<< HEAD
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_MANUAL
from . import SpeedtestCoordinator

=======
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
    ATTR_ISP,
    ATTR_JITTER,
    ATTR_PING,
    ATTR_SERVER,
    ATTR_UPLOAD,
    CONF_MANUAL,
    DOMAIN,
)
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
<<<<<<< HEAD
    coordinator = hass.data[DOMAIN][entry.entry_id]
    manual = entry.data.get(CONF_MANUAL, True)

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


class OoklaSpeedtestSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Speedtest sensor."""

=======
    coordinator: SpeedtestCoordinator = hass.data[DOMAIN][entry.entry_id]
    manual = entry.data.get(CONF_MANUAL, True)

    sensors = [
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_PING, "Ping", UnitOfTime.MILLISECONDS, "mdi:speedometer"
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
            coordinator, entry, ATTR_SERVER, "Server", None, "mdi:server"
        ),
        OoklaSpeedtestSensor(coordinator, entry, ATTR_ISP, "ISP", None, "mdi:web"),
    ]

    async_add_entities(sensors, update_before_add=not manual)


class OoklaSpeedtestSensor(CoordinatorEntity[SpeedtestCoordinator], SensorEntity):
    """Representation of a Speedtest sensor."""

    _attr_has_entity_name = True

>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
    def __init__(
        self,
        coordinator: SpeedtestCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
<<<<<<< HEAD
        unit: str,
=======
        unit: str | None,
        icon: str,
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
<<<<<<< HEAD
        self._attr_name = f"Speedtest {name}"
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_unit_of_measurement = unit
        _LOGGER.debug(f"Sensor initialized: {self._attr_name}")

    @property
    def state(self):
=======
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
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self._key)
