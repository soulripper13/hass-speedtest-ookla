"""Manager for Lovelace card resources."""

import logging
import shutil
from pathlib import Path

from homeassistant.components.lovelace import DOMAIN as LOVELACE_DOMAIN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

VERSION = "1.2.5"

# List of cards to manage
CARDS = [
    "ookla-speedtest-card.js",
    "ookla-speedtest-minimal.js", 
    "ookla-speedtest-compact.js",
    "ookla-speedtest-dashboard.js",
    "ookla-speedtest-card-simple.js",
]

WWW_SOURCE_DIR = Path(__file__).parent / "www"


async def async_setup_cards(hass: HomeAssistant) -> bool:
    """Set up the custom cards by copying to www folder.
    
    This ensures cards are accessible at /local/ookla_speedtest/
    """
    try:
        # Get path to www folder
        www_dir = Path(hass.config.path("www"))
        target_dir = www_dir / "ookla_speedtest"
        
        # Create www directory if it doesn't exist
        if not www_dir.exists():
            _LOGGER.info("Creating www directory")
            await hass.async_add_executor_job(www_dir.mkdir)
            
        # Create target directory
        if not target_dir.exists():
             await hass.async_add_executor_job(target_dir.mkdir)
        
        copied_count = 0
        for card in CARDS:
            source = WWW_SOURCE_DIR / card
            target = target_dir / card
            
            # Copy if source exists and (target missing or source newer)
            if source.exists():
                # We can do a simpler check: just copy. 
                # shutil.copy2 preserves metadata, so repeated copies are cheap if optimized by OS, 
                # but let's just copy to be sure we have latest version.
                await hass.async_add_executor_job(
                    shutil.copy2, source, target
                )
                copied_count += 1
        
        _LOGGER.debug(
            "Ookla Speedtest cards installed to www folder (%d files)",
            copied_count
        )
        return True
        
    except Exception as e:
        _LOGGER.error("Failed to set up cards: %s", e)
        return False


async def async_register_cards(hass: HomeAssistant) -> None:
    """Register Lovelace resources safely."""
    lovelace = hass.data.get(LOVELACE_DOMAIN)
    
    # Check if Lovelace is loaded
    if not lovelace:
        _LOGGER.debug("Lovelace not loaded, skipping resource registration")
        return

    # If resources aren't loaded yet, retry later
    if not getattr(lovelace, "resources", None) or not lovelace.resources.loaded:
        _LOGGER.debug("Lovelace resources not loaded, retrying in 5 seconds")
        async_call_later(hass, 5, lambda _: hass.async_create_task(async_register_cards(hass)))
        return
    
    resources = lovelace.resources
    
    for card in CARDS:
        base_url = f"/local/ookla_speedtest/{card}"
        full_url = f"{base_url}?v={VERSION}"
        
        # Find if resource exists (ignoring version param)
        found_resource = None
        for resource in resources.async_items():
            if resource["url"].split("?")[0] == base_url:
                found_resource = resource
                break
        
        if found_resource:
            # Update if version changed
            if found_resource["url"] != full_url:
                _LOGGER.info("Updating Lovelace resource %s to version %s", base_url, VERSION)
                try:
                    await resources.async_update_item(found_resource["id"], {
                        "res_type": "module",
                        "url": full_url
                    })
                except Exception as e:
                    _LOGGER.error("Failed to update resource %s: %s", base_url, e)
        else:
            # Create new
            _LOGGER.info("Auto-registering Lovelace resource: %s", full_url)
            try:
                await resources.async_create_item({
                    "res_type": "module",
                    "url": full_url
                })
            except Exception as e:
                _LOGGER.error("Failed to register %s: %s", full_url, e)


async def async_register_resources_service(hass: HomeAssistant) -> None:
    """Register a service to register Lovelace resources."""
    
    async def handle_register_resources(call):
        """Handle the service call."""
        await async_register_cards(hass)
    
    hass.services.async_register(
        DOMAIN,
        "register_card_resources",
        handle_register_resources,
    )


def get_card_info():
    """Get information about available cards."""
    return [
        {
            "name": "Ookla Speedtest",
            "type": "custom:ookla-speedtest-card",
            "description": "Full Ookla interface with radial gauges",
            "file": "ookla-speedtest-card.js"
        },
        {
            "name": "Ookla Speedtest - Minimal",
            "type": "custom:ookla-speedtest-minimal",
            "description": "Clean design with large typography",
            "file": "ookla-speedtest-minimal.js"
        },
        {
            "name": "Ookla Speedtest - Compact",
            "type": "custom:ookla-speedtest-compact",
            "description": "Small single-line card",
            "file": "ookla-speedtest-compact.js"
        },
        {
            "name": "Ookla Speedtest - Dashboard",
            "type": "custom:ookla-speedtest-dashboard",
            "description": "Full metrics with charts",
            "file": "ookla-speedtest-dashboard.js"
        }
    ]