"""Sensor platform for Ookla Speedtest integration."""

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_MANUAL
from . import SpeedtestCoordinator


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
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
