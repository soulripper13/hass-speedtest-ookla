import subprocess
import json
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from .const import DOMAIN, CONF_SERVER_ID, CONF_MANUAL, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL

class OoklaSpeedtestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ookla Speedtest."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        servers = await self._get_servers()

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Optional(CONF_SERVER_ID, default="closest"): vol.In(
                        {"closest": "Closest Server"} | {server["id"]: f"{server['name']} ({server['location']})" for server in servers}
                    ),
                    vol.Optional(CONF_MANUAL, default=True): bool,
                    vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
                }),
                errors=errors,
            )

        if user_input:
            return self.async_create_entry(
                title="Ookla Speedtest",
                data={
                    CONF_SERVER_ID: user_input[CONF_SERVER_ID],
                    CONF_MANUAL: user_input[CONF_MANUAL],
                    CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                }
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Optional(CONF_SERVER_ID, default="closest"): vol.In(
                    {"closest": "Closest Server"} | {server["id"]: f"{server['name']} ({server['location']})" for server in servers}
                ),
                vol.Optional(CONF_MANUAL, default=True): bool,
                vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
            }),
            errors=errors,
        )

    async def _get_servers(self):
        """Fetch the list of available Speedtest servers."""
        try:
            process = await self.hass.async_add_executor_job(
                lambda: subprocess.run(
                    ["/config/shell/list_servers.sh"],
                    capture_output=True,
                    text=True,
                    check=True
                )
            )
            servers = json.loads(process.stdout)
            return [
                {
                    "id": str(server["id"]),
                    "name": server["name"],
                    "location": f"{server['city']}, {server['country']}"
                }
                for server in servers["servers"]
            ]
        except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
            return []
