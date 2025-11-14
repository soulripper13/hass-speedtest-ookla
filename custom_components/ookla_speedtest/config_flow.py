"""Configuration flow for Ookla Speedtest integration."""

import subprocess
import json
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_SERVER_ID,
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class OoklaSpeedtestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ookla Speedtest."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        _LOGGER.debug("Starting config flow for Ookla Speedtest")

        # Run setup script if not already set up
        if not hasattr(self, "_setup_done"):
            await self._run_setup_script()
            self._setup_done = True

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

        schema = vol.Schema(
            {
                vol.Required(CONF_SERVER_ID, default="closest"): vol.In(server_options),
                vol.Optional("manual_server_id", default=""): str,
                vol.Optional(CONF_MANUAL, default=True): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): int,
            }
        )

        if user_input is None:
            _LOGGER.debug("Showing config form")
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
            )

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
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )
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

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_SERVER_ID,
                    default=self.config_entry.data.get(CONF_SERVER_ID, "closest"),
                ): vol.In(server_options),
                vol.Optional("manual_server_id", default=""): str,
                vol.Optional(
                    CONF_MANUAL,
                    default=self.config_entry.data.get(CONF_MANUAL, True),
                ): bool,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): int,
            }
        )

        if user_input is None:
            _LOGGER.debug("Showing options form")
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

        _LOGGER.debug(f"Received options input: {user_input}")
        server_id = user_input[CONF_SERVER_ID]
        if server_id == "manual":
            manual_id = user_input.get("manual_server_id", "").strip()
            if not manual_id or not manual_id.isdigit():
                errors["manual_server_id"] = "Valid numeric server ID required when selecting Manual Server ID"
                return self.async_show_form(
                    step_id="init",
                    data_schema=schema,
                    errors=errors,
                )
            server_id = manual_id
        elif server_id != "closest" and (not server_id or not server_id.isdigit()):
            errors["server_id"] = "Invalid server ID selected"
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

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
