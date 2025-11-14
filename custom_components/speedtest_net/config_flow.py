"""Config flow for Speedtest.net integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    DOMAIN,
    CONF_SCAN_INTERVAL,
    CONF_AUTO_UPDATE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_AUTO_UPDATE,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Optional(
            CONF_SCAN_INTERVAL,
            description={"suggested_value": DEFAULT_SCAN_INTERVAL},
        ): int,
        vol.Optional(
            CONF_AUTO_UPDATE, default=DEFAULT_AUTO_UPDATE
        ): bool,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Speedtest.net."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Speedtest.net", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
        )

class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Speedtest.net options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        auto_update = self.config_entry.options.get(CONF_AUTO_UPDATE, DEFAULT_AUTO_UPDATE)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        description={"suggested_value": scan_interval},
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=60,
                            max=86400,
                            unit_of_measurement="seconds",
                        )
                    ),
                    vol.Optional(
                        CONF_AUTO_UPDATE, default=auto_update
                    ): bool,
                }
            ),
            description_placeholders={
                "auto_update_desc": "Enable automatic updates at the interval below, or disable for manual-only (use service to trigger)."
            },
        )
