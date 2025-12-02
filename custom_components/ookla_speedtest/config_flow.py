"""Configuration flow for Ookla Speedtest integration."""

<<<<<<< HEAD
import subprocess
import json
import logging
=======
from __future__ import annotations

import logging
import subprocess
from typing import Any


import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
<<<<<<< HEAD
    DOMAIN,
    CONF_SERVER_ID,
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)
=======
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    CONF_SERVER_ID,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    INTEGRATION_SHELL_DIR,
)
from .helpers import get_speedtest_servers, validate_server_id
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)

_LOGGER = logging.getLogger(__name__)

class OoklaSpeedtestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ookla Speedtest."""

    VERSION = 1

<<<<<<< HEAD
    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting config flow for Ookla Speedtest")

=======
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
        # Run setup script if not already set up
        if not hasattr(self, "_setup_done"):
            await self._run_setup_script()
            self._setup_done = True

        errors = {}
<<<<<<< HEAD
        servers = await self._get_servers()
        if not servers:
            _LOGGER.warning("No servers retrieved; defaulting to Closest Server option")
            server_options = {"closest": "Closest Server"}
        else:
            _LOGGER.debug(f"Retrieved {len(servers)} servers")
            server_options = {"closest": "Closest Server"} | {
                server["id"]: f"{server['name']} ({server['location']} - {server['distance']} km)"
                for server in servers
            }
            server_options["manual"] = "Manual Server ID"

        schema = vol.Schema(
            {
                vol.Required(CONF_SERVER_ID, default="closest"): vol.In(server_options),
                vol.Optional("manual_server_id", default=""): str,
                vol.Optional(CONF_MANUAL, default=True): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): int,
=======
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
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
            }
        )

        if user_input is None:
<<<<<<< HEAD
            _LOGGER.debug("Showing config form")
=======
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
            )

<<<<<<< HEAD
        if user_input:
            _LOGGER.debug(f"Received user input: {user_input}")
            server_id = user_input[CONF_SERVER_ID]
            if server_id == "manual":
                manual_id = user_input.get("manual_server_id", "").strip()
                if not manual_id or not manual_id.isdigit():
                    errors["manual_server_id"] = "Valid numeric server ID required when selecting Manual Server ID"
                    return self.async_show_form(
                        step_id="user",
                        data_schema=schema,
                        errors=errors,
                    )
                server_id = manual_id
            elif server_id != "closest" and (not server_id or not server_id.isdigit()):
                errors["server_id"] = "Invalid server ID selected"
=======
        # Validate and process server ID
        server_id = user_input[CONF_SERVER_ID]
        if server_id == "manual":
            manual_id = user_input.get("manual_server_id", "").strip()
            if not validate_server_id(manual_id):
                errors["manual_server_id"] = (
                    "Valid numeric server ID required when selecting Manual Server ID"
                )
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
                return self.async_show_form(
                    step_id="user",
                    data_schema=schema,
                    errors=errors,
                )
<<<<<<< HEAD

            config_data = {
                CONF_SERVER_ID: server_id,
                CONF_MANUAL: user_input[CONF_MANUAL],
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
            }
            _LOGGER.debug(f"Saving config entry with data: {config_data}")
            return self.async_create_entry(
                title="Ookla Speedtest",
                data=config_data,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OoklaSpeedtestOptionsFlow(config_entry)

    async def _run_setup_script(self):
        """Run the setup script to prepare the environment."""
        _LOGGER.debug("Running setup script")
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    ["/config/custom_components/ookla_speedtest/shell/setup_speedtest.sh"],
=======
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
        return OoklaSpeedtestOptionsFlow(config_entry)

    async def _run_setup_script(self) -> None:
        """Run the setup script to prepare the environment."""
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    [f"{INTEGRATION_SHELL_DIR}/setup_speedtest.sh"],
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )
<<<<<<< HEAD
            _LOGGER.debug(f"Setup script output: {process.stdout}")
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Setup script failed: {e.stderr}")
            raise config_entries.ConfigFlowError(
                "Failed to run setup script. Check logs and ensure /config/shell/ is writable. "
                "Ensure scripts are executable with 'chmod +x /config/custom_components/ookla_speedtest/shell/*.sh'."
            )

    async def _get_servers(self):
        """Fetch the list of 10 closest Speedtest servers."""
        _LOGGER.debug("Fetching 10 closest Speedtest servers")
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    ["/config/shell/speedtest.bin", "--servers", "--format=json", "--accept-license", "--accept-gdpr"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )
            raw_output = process.stdout
            _LOGGER.debug(f"Raw server list output: {raw_output[:500]}...")
            servers_data = json.loads(raw_output)
            servers = servers_data.get("servers", [])
            _LOGGER.debug(f"Parsed {len(servers)} servers")
            # Sort by distance and take the 10 closest
            sorted_servers = sorted(servers, key=lambda x: x.get("distance", float("inf")))
            result = []
            for server in sorted_servers[:10]:
                # Safely access server data with fallbacks
                city = server.get("city", server.get("location", "Unknown City"))
                country = server.get("country", server.get("region", "Unknown Country"))
                name = server.get("name", "Unknown Server")
                distance = round(server.get("distance", 0), 2)
                server_id = str(server.get("id", ""))
                if not server_id:
                    _LOGGER.warning(f"Skipping server with missing ID: {name}")
                    continue
                result.append(
                    {
                        "id": server_id,
                        "name": name,
                        "location": f"{city}, {country}",
                        "distance": distance,
                    }
                )
            _LOGGER.debug(f"Returning {len(result)} valid servers")
            return result
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Failed to fetch server list: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Failed to parse server list JSON: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Unexpected error fetching servers: {str(e)}")
            return []

class OoklaSpeedtestOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Ookla Speedtest."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        pass  # No explicit config_entry assignment

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        _LOGGER.debug("Starting options flow for Ookla Speedtest")

        errors = {}
        servers = await self._get_servers()
        if not servers:
            _LOGGER.warning("No servers retrieved; defaulting to Closest Server option")
            server_options = {"closest": "Closest Server"}
        else:
            _LOGGER.debug(f"Retrieved {len(servers)} servers")
            server_options = {"closest": "Closest Server"} | {
                server["id"]: f"{server['name']} ({server['location']} - {server['distance']} km)"
                for server in servers
            }
            server_options["manual"] = "Manual Server ID"
=======
            _LOGGER.debug("Setup script completed: %s", process.stdout)
        except subprocess.CalledProcessError as e:
            _LOGGER.error("Setup script failed: %s", e.stderr)
            raise config_entries.ConfigFlowError(
                "Failed to run setup script. Check logs and ensure /config/shell/ is writable. "
                f"Ensure scripts are executable with 'chmod +x {INTEGRATION_SHELL_DIR}/*.sh'."
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
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SERVER_ID,
<<<<<<< HEAD
                    default=self.config_entry.data.get(CONF_SERVER_ID, "closest"),
=======
                    default=current_server_id,
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
                ): vol.In(server_options),
                vol.Optional("manual_server_id", default=""): str,
                vol.Optional(
                    CONF_MANUAL,
<<<<<<< HEAD
                    default=self.config_entry.data.get(CONF_MANUAL, True),
                ): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
=======
                    default=current_manual,
                ): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=current_scan_interval,
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
                ): int,
            }
        )

        if user_input is None:
<<<<<<< HEAD
            _LOGGER.debug("Showing options form")
=======
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

<<<<<<< HEAD
        _LOGGER.debug(f"Received options input: {user_input}")
        server_id = user_input[CONF_SERVER_ID]
        if server_id == "manual":
            manual_id = user_input.get("manual_server_id", "").strip()
            if not manual_id or not manual_id.isdigit():
                errors["manual_server_id"] = "Valid numeric server ID required when selecting Manual Server ID"
=======
        # Validate and process server ID
        server_id = user_input[CONF_SERVER_ID]
        if server_id == "manual":
            manual_id = user_input.get("manual_server_id", "").strip()
            if not validate_server_id(manual_id):
                errors["manual_server_id"] = (
                    "Valid numeric server ID required when selecting Manual Server ID"
                )
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
                return self.async_show_form(
                    step_id="init",
                    data_schema=schema,
                    errors=errors,
                )
            server_id = manual_id
<<<<<<< HEAD
        elif server_id != "closest" and (not server_id or not server_id.isdigit()):
=======
        elif not validate_server_id(server_id):
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
            errors["server_id"] = "Invalid server ID selected"
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

<<<<<<< HEAD
        # Update the config entry with new data
        updated_data = {
            CONF_SERVER_ID: server_id,
            CONF_MANUAL: user_input[CONF_MANUAL],
            CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
        }
        _LOGGER.debug(f"Updating config entry with data: {updated_data}")
        self.hass.config_entries.async_update_entry(
            self.config_entry,
            data=updated_data,
        )

        return self.async_create_entry(title=None, data={})

    async def _get_servers(self):
        """Fetch the list of 10 closest Speedtest servers."""
        _LOGGER.debug("Fetching 10 closest Speedtest servers for options flow")
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    ["/config/shell/speedtest.bin", "--servers", "--format=json", "--accept-license", "--accept-gdpr"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )
            raw_output = process.stdout
            _LOGGER.debug(f"Raw server list output: {raw_output[:500]}...")
            servers_data = json.loads(raw_output)
            servers = servers_data.get("servers", [])
            _LOGGER.debug(f"Parsed {len(servers)} servers")
            # Sort by distance and take the 10 closest
            sorted_servers = sorted(servers, key=lambda x: x.get("distance", float("inf")))
            result = []
            for server in sorted_servers[:10]:
                # Safely access server data with fallbacks
                city = server.get("city", server.get("location", "Unknown City"))
                country = server.get("country", server.get("region", "Unknown Country"))
                name = server.get("name", "Unknown Server")
                distance = round(server.get("distance", 0), 2)
                server_id = str(server.get("id", ""))
                if not server_id:
                    _LOGGER.warning(f"Skipping server with missing ID: {name}")
                    continue
                result.append(
                    {
                        "id": server_id,
                        "name": name,
                        "location": f"{city}, {country}",
                        "distance": distance,
                    }
                )
            _LOGGER.debug(f"Returning {len(result)} valid servers")
            return result
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Failed to fetch server list: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Failed to parse server list JSON: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Unexpected error fetching servers: {str(e)}")
            return []
=======
        # Return options data (not updating data directly)
        return self.async_create_entry(
            title="",
            data={
                CONF_SERVER_ID: server_id,
                CONF_MANUAL: user_input[CONF_MANUAL],
                CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
            },
        )
>>>>>>> 753d9b0 (Fix config flow 500 error and add user-friendly descriptions)
