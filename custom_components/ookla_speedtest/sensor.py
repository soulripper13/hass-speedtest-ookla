"""Sensor platform for Ookla Speedtest integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    Platform,
    UnitOfDataRate,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import RegistryEntryDisabler, async_get
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import SpeedtestCoordinator
from .const import (
    ATTR_BUFFERBLOAT_GRADE,
    ATTR_DATE_LAST_TEST,
    ATTR_DL_PCT,
    ATTR_DOWNLOAD,
    ATTR_DOWNLOAD_LATENCY_HIGH,
    ATTR_DOWNLOAD_LATENCY_IQM,
    ATTR_DOWNLOAD_LATENCY_JITTER,
    ATTR_DOWNLOAD_LATENCY_LOW,
    ATTR_ISP,
    ATTR_JITTER,
    ATTR_PING,
    ATTR_PING_HIGH,
    ATTR_PING_LOW,
    ATTR_RESULT_URL,
    ATTR_SERVER,
    ATTR_UL_PCT,
    ATTR_UPLOAD,
    ATTR_UPLOAD_LATENCY_HIGH,
    ATTR_UPLOAD_LATENCY_IQM,
    ATTR_UPLOAD_LATENCY_JITTER,
    ATTR_UPLOAD_LATENCY_LOW,
    CONF_ENABLE_COMPLIANCE_SENSORS,
    CONF_ENABLE_LATENCY_SENSORS,
    DEFAULT_ENABLE_COMPLIANCE,
    DEFAULT_ENABLE_LATENCY,
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

    # Get configuration options
    enabled_latency = entry.options.get(
        CONF_ENABLE_LATENCY_SENSORS,
        entry.data.get(CONF_ENABLE_LATENCY_SENSORS, DEFAULT_ENABLE_LATENCY),
    )
    enabled_compliance = entry.options.get(
        CONF_ENABLE_COMPLIANCE_SENSORS,
        entry.data.get(CONF_ENABLE_COMPLIANCE_SENSORS, DEFAULT_ENABLE_COMPLIANCE),
    )

    sensors = [
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_PING,
            "Ping",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_PING_LOW,
            "Ping Min",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_PING_HIGH,
            "Ping Max",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_DOWNLOAD_LATENCY_IQM,
            "Download Ping",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_DOWNLOAD_LATENCY_LOW,
            "Download Ping Min",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_DOWNLOAD_LATENCY_HIGH,
            "Download Ping Max",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UPLOAD_LATENCY_IQM,
            "Upload Ping",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UPLOAD_LATENCY_LOW,
            "Upload Ping Min",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UPLOAD_LATENCY_HIGH,
            "Upload Ping Max",
            UnitOfTime.MILLISECONDS,
            "mdi:speedometer",
            enabled_default=enabled_latency,
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
            ATTR_DL_PCT,
            "Download Plan Compliance",
            PERCENTAGE,
            "mdi:percent",
            enabled_default=enabled_compliance,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UL_PCT,
            "Upload Plan Compliance",
            PERCENTAGE,
            "mdi:percent",
            enabled_default=enabled_compliance,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_BUFFERBLOAT_GRADE,
            "Bufferbloat Grade",
            None,
            "mdi:check-network",
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
            enabled_default=enabled_compliance,
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_UPLOAD_LATENCY_JITTER,
            "Upload Jitter",
            UnitOfTime.MILLISECONDS,
            "mdi:pulse",
            enabled_default=enabled_compliance,
        ),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_SERVER, "Server", None, "mdi:server"
        ),
        OoklaSpeedtestSensor(coordinator, entry, ATTR_ISP, "ISP", None, "mdi:web"),
        OoklaSpeedtestSensor(
            coordinator, entry, ATTR_RESULT_URL, "Result URL", None, "mdi:link"
        ),
        OoklaSpeedtestSensor(
            coordinator,
            entry,
            ATTR_DATE_LAST_TEST,
            "Last Test",
            None,
            "mdi:clock",
        ),
    ]

    # Manage entity registry state based on configuration options
    ent_reg = async_get(hass)
    
    latency_keys = {
        ATTR_PING_LOW, ATTR_PING_HIGH,
        ATTR_DOWNLOAD_LATENCY_IQM, ATTR_DOWNLOAD_LATENCY_LOW, ATTR_DOWNLOAD_LATENCY_HIGH,
        ATTR_UPLOAD_LATENCY_IQM, ATTR_UPLOAD_LATENCY_LOW, ATTR_UPLOAD_LATENCY_HIGH
    }
    compliance_keys = {
        ATTR_DL_PCT, ATTR_UL_PCT,
        ATTR_DOWNLOAD_LATENCY_JITTER, ATTR_UPLOAD_LATENCY_JITTER
    }

    for sensor in sensors:
        # Construct unique_id correctly to match __init__
        unique_id = f"{entry.entry_id}_{sensor._key}"
        entity_id = ent_reg.async_get_entity_id(Platform.SENSOR, DOMAIN, unique_id)
        
        if not entity_id:
            continue
            
        registry_entry = ent_reg.async_get(entity_id)
        if not registry_entry:
            continue
            
        # Determine desired state
        should_be_enabled = True # Default for core sensors
        
        if sensor._key in latency_keys:
            should_be_enabled = enabled_latency
        elif sensor._key in compliance_keys:
            should_be_enabled = enabled_compliance
            
        # Only touch if not user-controlled
        if registry_entry.disabled_by != RegistryEntryDisabler.USER:
            if should_be_enabled and registry_entry.disabled:
                # Enable it
                ent_reg.async_update_entity(entity_id, disabled_by=None)
            elif not should_be_enabled and not registry_entry.disabled:
                # Disable it
                ent_reg.async_update_entity(entity_id, disabled_by=RegistryEntryDisabler.INTEGRATION)

    # Don't update before adding to avoid blocking HA startup
    async_add_entities(sensors, update_before_add=False)


class OoklaSpeedtestSensor(CoordinatorEntity[SpeedtestCoordinator], RestoreSensor):
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
        enabled_default: bool = True,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = icon
        self._attr_entity_registry_enabled_default = enabled_default
        self._restored_value: Any = None

        # Set state class for numeric sensors to enable statistics
        if key in (
            ATTR_PING,
            ATTR_DOWNLOAD,
            ATTR_UPLOAD,
            ATTR_JITTER,
            ATTR_DL_PCT,
            ATTR_UL_PCT,
        ):
            self._attr_state_class = SensorStateClass.MEASUREMENT

        if key == ATTR_DATE_LAST_TEST:
            self._attr_device_class = SensorDeviceClass.TIMESTAMP

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
        if self.coordinator.data is not None and self._key in self.coordinator.data:
            return self.coordinator.data[self._key]
        return self._restored_value

    def _parse_restored_state(self, state_str: str) -> Any:
        """Parse restored state from raw state string."""
        if self._key == ATTR_DATE_LAST_TEST:
            return dt_util.parse_datetime(state_str)
        if self._key in (
            ATTR_BUFFERBLOAT_GRADE,
            ATTR_SERVER,
            ATTR_ISP,
            ATTR_RESULT_URL,
        ):
            return state_str
        try:
            return float(state_str)
        except (ValueError, TypeError):
            return None

    async def async_added_to_hass(self) -> None:
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if self.coordinator.data is None or self._key not in self.coordinator.data:
            if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
                self._restored_value = last_sensor_data.native_value
            elif (last_state := await self.async_get_last_state()) is not None:
                if last_state.state not in (STATE_UNKNOWN, STATE_UNAVAILABLE):
                    self._restored_value = self._parse_restored_state(last_state.state)

            if self._restored_value is not None:
                if self.coordinator.data is None:
                    self.coordinator.data = {}
                self.coordinator.data[self._key] = self._restored_value

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if self.coordinator.data is not None and self._key in self.coordinator.data:
            self._restored_value = self.coordinator.data[self._key]
        super()._handle_coordinator_update()
