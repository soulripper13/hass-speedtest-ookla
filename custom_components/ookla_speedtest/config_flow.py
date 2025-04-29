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
                server["id"]: f"{server['name']} ({server['location']})"
                for server in servers
            }

        schema = vol.Schema(
            {
                vol.Optional(CONF_SERVER_ID, default="closest"): vol.In(server_options),
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
            if server_id == "closest" and user_input.get("manual_server_id"):
                server_id = user_input["manual_server_id"]
            return self.async_create_entry(
                title="Ookla Speedtest",
                data={
                    CONF_SERVER_ID: server_id,
                    CONF_MANUAL: user_input[CONF_MANUAL],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

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
                "Failed to run setup script. Check logs and ensure /config/shell/ is writable."
            )

    async def _get_servers(self):
        """Fetch the list of available Speedtest servers."""
        _LOGGER.debug("Fetching Speedtest server list")
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    ["/config/shell/list_servers.sh"],
                    capture_output=True,
                    text=True,
                    check=True,
                )
            )
            _LOGGER.debug(f"Server list command output: {process.stdout[:100]}...")
            servers = json.loads(process.stdout)
            _LOGGER.debug(f"Parsed {len(servers.get('servers', []))} servers")
            return [
                {
                    "id": str(server["id"]),
                    "name": server["name"],
                    "location": f"{server['city']}, {server['country']}",
                }
                for server in servers["servers"]
            ]
        except subprocess.CalledProcessError as e:
            _LOGGER.error(f"Failed to fetch server list: {e.stderr}")
            return []
        except json.JSONDecodeError as e:
            _LOGGER.error(f"Failed to parse server list JSON: {e}")
            return []
        except Exception as e:
            _LOGGER.error(f"Unexpected error fetching servers: {e}")
            return []
