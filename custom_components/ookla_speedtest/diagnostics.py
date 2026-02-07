"""Diagnostics support for Ookla Speedtest."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import SpeedtestCoordinator
from .const import DOMAIN

TO_REDACT = {"manual_server_id", "result_url"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: SpeedtestCoordinator = hass.data[DOMAIN][entry.entry_id]

    diagnostics_data = {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "coordinator_data": async_redact_data(coordinator.data, TO_REDACT),
    }

    return diagnostics_data
