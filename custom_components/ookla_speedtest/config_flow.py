"""Configuration flow for Ookla Speedtest integration."""
from __future__ import annotations

import logging
import subprocess
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    CONF_SERVER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    INTEGRATION_SHELL_DIR,
)
from .helpers import get_speedtest_servers, validate_server_id

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class OoklaSpeedtestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ookla Speedtest."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        # Run setup script if not already set up
        if not hasattr(self, "_setup_done"):
            await self._run_setup_script()
            self._setup_done = True

        errors = {}
        servers = await get_speedtest_servers(self.hass)
        server_options = self._build_server_options(servers)

        schema = vol.Schema(
            {
                vol.Required(CONF_SERVER_ID, default="closest"): vol.In(
                    server_options
                ),
                vol.Optional("manual_server_id", default=""): str,
                vol.Optional(CONF_MANUAL, default=True): bool,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
            )

        # Validate and process server ID
        server_id = user_input[CONF_SERVER_ID]
        if server_id == "manual":
            manual_id = user_input.get("manual_server_id", "").strip()
            if not validate_server_id(manual_id):
                errors["manual_server_id"] = (
                    "Valid numeric server ID required when selecting Manual Server ID"
                )
                return self.async_show_form(
                    step_id="user",
                    data_schema=schema,
                    errors=errors,
                )
            server_id = manual_id
        elif not validate_server_id(server_id):
            errors["server_id"] = "Invalid server ID selected"
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
            )

        config_data = {
            CONF_SERVER_ID: server_id,
            CONF_MANUAL: user_input[CONF_MANUAL],
            CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
        }
        return self.async_create_entry(
            title="Ookla Speedtest",
            data=config_data,
        )

    @staticmethod
    def _build_server_options(servers: list[dict[str, Any]]) -> dict[str, str]:
        """Build server options dictionary for the config flow."""
        if not servers:
            _LOGGER.warning("No servers retrieved; defaulting to Closest Server option")
            return {"closest": "Closest Server"}

        server_options = {"closest": "Closest Server"}
        server_options.update(
            {
                server["id"]: (
                    f"{server['name']} ({server['location']} - {server['distance']} km)"
                )
                for server in servers
            }
        )
        server_options["manual"] = "Manual Server ID"
        return server_options

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OoklaSpeedtestOptionsFlow:
        """Get the options flow for this handler."""
        return OoklaSpeedtestOptionsFlow()

    async def _run_setup_script(self) -> None:
        """Run the setup script to prepare the environment."""
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    [f"{INTEGRATION_SHELL_DIR}/setup_speedtest.sh"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )
            _LOGGER.debug("Setup script completed: %s", process.stdout)
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Setup script failed: %s", e.stderr)
            _LOGGER.error(
                "Failed to run setup script. Check logs and ensure /config/shell/ is writable. "
                "Ensure scripts are executable with 'chmod +x %s/*.sh'.",
                INTEGRATION_SHELL_DIR,
            )


class OoklaSpeedtestOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Ookla Speedtest."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}
        servers = await get_speedtest_servers(self.hass)
        server_options = OoklaSpeedtestConfigFlow._build_server_options(servers)

        # Get defaults from options first, then fall back to data
        current_server_id = self.config_entry.options.get(
            CONF_SERVER_ID, self.config_entry.data.get(CONF_SERVER_ID, "closest")
        )
        current_manual = self.config_entry.options.get(
            CONF_MANUAL, self.config_entry.data.get(CONF_MANUAL, True)
        )
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SERVER_ID,
                    default=current_server_id,
                ): vol.In(server_options),
                vol.Optional("manual_server_id", default=""): str,
                vol.Optional(
                    CONF_MANUAL,
                    default=current_manual,
                ): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
                ): int,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

        # Validate and process server ID
        server_id = user_input[CONF_SERVER_ID]
        if server_id == "manual":
            manual_id = user_input.get("manual_server_id", "").strip()
            if not validate_server_id(manual_id):
                errors["manual_server_id"] = (
                    "Valid numeric server ID required when selecting Manual Server ID"
                )
                return self.async_show_form(
                    step_id="init",
                    data_schema=schema,
                    errors=errors,
                )
            server_id = manual_id
        elif not validate_server_id(server_id):
            errors["server_id"] = "Invalid server ID selected"
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

        # Return options data (not updating data directly)
        return self.async_create_entry(
            title="",
            data={
                CONF_SERVER_ID: server_id,
                CONF_MANUAL: user_input[CONF_MANUAL],
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
            },
        )
