"""Initialize the Ookla Speedtest integration."""

import logging
import os
import stat

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR]


# Set execute permissions on shell scripts
SHELL_SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "shell")
if os.path.isdir(SHELL_SCRIPT_DIR):
    for script_name in os.listdir(SHELL_SCRIPT_DIR):
        script_path = os.path.join(SHELL_SCRIPT_DIR, script_name)
        if script_path.endswith(".sh"):
            try:
                st = os.stat(script_path)
                os.chmod(script_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                _LOGGER.debug("Made shell script %s executable.", script_path)
            except OSError as e:
                _LOGGER.error("Failed to make shell script %s executable: %s", script_path, e)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ookla Speedtest from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
