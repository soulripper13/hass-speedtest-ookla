"""The Speedtest.net integration."""
import asyncio
import logging
import os
import platform
import tarfile
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    DOMAIN,
    CONF_AUTO_UPDATE,
    CONF_SCAN_INTERVAL,
    DEFAULT_AUTO_UPDATE,
    DEFAULT_SCAN_INTERVAL,
    BINARY_NAME,
    BINARY_URL,
    BINARY_DIR,
)

PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Speedtest.net from a config entry."""
    # Download binary if not present
    binary_path = await _download_binary(hass, entry)
    if not binary_path:
        _LOGGER.error("Failed to download/extract Speedtest CLI binary")
        return False

    # Store binary path in hass.data (accessed async by platforms)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"binary_path": binary_path}

    # Forward to platforms (async loads sensor.py)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register service for manual trigger
    _register_services(hass)

    # Listen for options changes
    entry.add_update_listener(async_options_updated)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

async def async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)

@callback
def _register_services(hass: HomeAssistant) -> None:
    """Register the services."""

    async def async_perform_test(service_call) -> None:
        """Manually trigger speedtest via coordinator."""
        hass_data = hass.data.get(DOMAIN)
        if not hass_data:
            _LOGGER.warning("No Speedtest.net data found")
            return

        coordinator = None
        for entry_id, data in hass_data.items():
            coordinator = data.get("coordinator")
            if coordinator:
                break

        if coordinator:
            try:
                await coordinator.async_request_refresh()
                _LOGGER.info("Manually triggered refresh on Speedtest.net coordinator")
            except Exception as err:
                _LOGGER.error("Failed to refresh Speedtest.net: %s", err)
        else:
            _LOGGER.warning("No Speedtest.net coordinator found to update")

    async def async_update_binary(service_call) -> None:
        """Update the Speedtest CLI binary."""
        await _update_binary(hass)

    hass.services.async_register(DOMAIN, "perform_test", async_perform_test)
    hass.services.async_register(DOMAIN, "update_binary", async_update_binary)

async def _update_binary(hass: HomeAssistant) -> None:
    """Update the Speedtest CLI binary."""
    binary_dir = Path(hass.config.path(BINARY_DIR))
    binary_path = binary_dir / BINARY_NAME

    if binary_path.exists():
        binary_path.unlink()
        _LOGGER.debug("Removed existing Speedtest CLI binary at %s", binary_path)

    entry = next(iter(hass.config_entries.async_entries(DOMAIN)))
    binary_path = await _download_binary(hass, entry)
    if not binary_path:
        _LOGGER.error("Failed to download/extract Speedtest CLI binary")
        return

    _LOGGER.info("Speedtest CLI binary updated successfully. Restarting integration.")
    await hass.config_entries.async_reload(entry.entry_id)

async def _download_binary(hass: HomeAssistant, entry: ConfigEntry) -> str | None:
    """Download and extract the Speedtest CLI binary if not present."""
    binary_dir = Path(hass.config.path(BINARY_DIR))
    binary_dir.mkdir(exist_ok=True)
    binary_path = binary_dir / BINARY_NAME

    if binary_path.exists() and os.access(str(binary_path), os.X_OK):
        _LOGGER.debug("Speedtest CLI binary already exists and is executable at %s", binary_path)
        return str(binary_path)

    # Download tgz
    session = async_get_clientsession(hass)
    tgz_path = binary_dir / "speedtest.tgz"
    try:
        async with session.get(BINARY_URL) as resp:
            if resp.status != 200:
                _LOGGER.error("Failed to download tgz from %s: %s", BINARY_URL, resp.status)
                return None
            content = await resp.read()
        tgz_path.write_bytes(content)
        _LOGGER.debug("Downloaded Speedtest CLI tgz to %s", tgz_path)

        # Extract tgz
        with tarfile.open(tgz_path, 'r:gz') as tf:
            tf.extractall(binary_dir)
        _LOGGER.debug("Extracted Speedtest CLI tgz contents to %s", binary_dir)

        # Find and chmod the binary
        extracted_binary = binary_dir / BINARY_NAME
        if not extracted_binary.exists():
            _LOGGER.error("No executable found in tgz")
            return None

        os.chmod(str(extracted_binary), 0o755)
        tgz_path.unlink()  # Clean up tgz

        # Log the version of the downloaded binary
        try:
            proc = await asyncio.create_subprocess_exec(
                str(extracted_binary),
                "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                version_output = stdout.decode("utf-8", errors="ignore").strip()
                _LOGGER.info("Downloaded Speedtest CLI binary version: %s", version_output)
            else:
                _LOGGER.warning(
                    "Could not get version of downloaded Speedtest CLI binary. Stderr: %s",
                    stderr.decode("utf-8", errors="ignore").strip(),
                )
        except Exception as version_err:
            _LOGGER.warning("Error getting version of downloaded Speedtest CLI binary: %s", version_err)

        _LOGGER.info("Extracted and made executable Speedtest CLI binary at %s", extracted_binary)
        return str(extracted_binary)

    except Exception as err:
        _LOGGER.error("Error downloading/extracting binary: %s", err)
        if tgz_path.exists():
            tgz_path.unlink()
        return None
