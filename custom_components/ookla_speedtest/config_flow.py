"""Configuration flow for Ookla Speedtest integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_ENABLE_COMPLIANCE_SENSORS,
    CONF_FALLBACK_TO_CLOSEST,
    CONF_ENABLE_LATENCY_SENSORS,
    CONF_ISP_DL_SPEED,
    CONF_ISP_UL_SPEED,
    CONF_MANUAL,
    CONF_SCAN_INTERVAL,
    CONF_SERVER_ID,
    CONF_START_TIME,
    DEFAULT_ENABLE_COMPLIANCE,
    DEFAULT_FALLBACK_TO_CLOSEST,
    DEFAULT_ENABLE_LATENCY,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .helpers import (
    get_speedtest_servers,
    validate_server_id,
    validate_time_format,
)
from .binary_manager import async_setup_speedtest

_LOGGER = logging.getLogger(__name__)


@config_entries.HANDLERS.register(DOMAIN)
class OoklaSpeedtestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ookla Speedtest."""

    VERSION = 1

    @staticmethod
    def _duration_to_minutes(duration: dict[str, int]) -> float:
        """Convert duration dict to minutes."""
        return (
            duration.get("days", 0) * 1440
            + duration.get("hours", 0) * 60
            + duration.get("minutes", 0)
            + duration.get("seconds", 0) / 60
        )

    @staticmethod
    def _minutes_to_duration(minutes: float) -> dict[str, int]:
        """Convert minutes to duration dict."""
        seconds = int(minutes * 60)
        return {
            "days": seconds // 86400,
            "hours": (seconds % 86400) // 3600,
            "minutes": (seconds % 3600) // 60,
            "seconds": seconds % 60,
        }

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
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=self._minutes_to_duration(DEFAULT_SCAN_INTERVAL),
                ): selector.DurationSelector(
                    selector.DurationSelectorConfig(enable_day=True)
                ),
                vol.Optional(CONF_START_TIME): selector.TimeSelector(),
                vol.Optional(CONF_ISP_DL_SPEED): vol.Coerce(float),
                vol.Optional(CONF_ISP_UL_SPEED): vol.Coerce(float),
                vol.Optional(
                    CONF_ENABLE_LATENCY_SENSORS, default=DEFAULT_ENABLE_LATENCY
                ): bool,
                vol.Optional(
                    CONF_ENABLE_COMPLIANCE_SENSORS, default=DEFAULT_ENABLE_COMPLIANCE
                ): bool,
                vol.Optional(
                    CONF_FALLBACK_TO_CLOSEST, default=DEFAULT_FALLBACK_TO_CLOSEST
                ): bool,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                errors=errors,
            )

        # Process input
        scan_interval_input = user_input[CONF_SCAN_INTERVAL]
        if isinstance(scan_interval_input, dict):
            scan_interval = self._duration_to_minutes(scan_interval_input)
        else:
            scan_interval = scan_interval_input  # Should not happen with selector

        start_time = user_input.get(CONF_START_TIME)

        # Validate time format (selector should enforce, but safe to keep)
        if start_time and not validate_time_format(start_time):
            errors[CONF_START_TIME] = "Invalid time format"
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
            CONF_SCAN_INTERVAL: scan_interval,
            CONF_START_TIME: start_time,
            CONF_ISP_DL_SPEED: user_input.get(CONF_ISP_DL_SPEED),
            CONF_ISP_UL_SPEED: user_input.get(CONF_ISP_UL_SPEED),
            CONF_ENABLE_LATENCY_SENSORS: user_input.get(
                CONF_ENABLE_LATENCY_SENSORS, DEFAULT_ENABLE_LATENCY
            ),
            CONF_ENABLE_COMPLIANCE_SENSORS: user_input.get(
                CONF_ENABLE_COMPLIANCE_SENSORS, DEFAULT_ENABLE_COMPLIANCE
            ),
            CONF_FALLBACK_TO_CLOSEST: user_input.get(
                CONF_FALLBACK_TO_CLOSEST, DEFAULT_FALLBACK_TO_CLOSEST
            ),
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
                    f"{server['name']} ({server['location']})"
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
        """Set up the speedtest binary using pure Python."""
        try:
            await async_setup_speedtest(self.hass)
            _LOGGER.debug("Speedtest binary setup completed successfully")
        except Exception as e:
            _LOGGER.error("Failed to set up speedtest binary: %s", e)


class OoklaSpeedtestOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Ookla Speedtest."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}
        servers = await get_speedtest_servers(self.hass)
        server_options = OoklaSpeedtestConfigFlow._build_server_options(servers)

        # Get defaults
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
        current_start_time = self.config_entry.options.get(
            CONF_START_TIME,
            self.config_entry.data.get(CONF_START_TIME, None),
        )
        current_isp_dl = self.config_entry.options.get(
            CONF_ISP_DL_SPEED,
            self.config_entry.data.get(CONF_ISP_DL_SPEED),
        )
        current_isp_ul = self.config_entry.options.get(
            CONF_ISP_UL_SPEED,
            self.config_entry.data.get(CONF_ISP_UL_SPEED),
        )
        current_enable_latency = self.config_entry.options.get(
            CONF_ENABLE_LATENCY_SENSORS,
            self.config_entry.data.get(
                CONF_ENABLE_LATENCY_SENSORS, DEFAULT_ENABLE_LATENCY
            ),
        )
        current_enable_compliance = self.config_entry.options.get(
            CONF_ENABLE_COMPLIANCE_SENSORS,
            self.config_entry.data.get(
                CONF_ENABLE_COMPLIANCE_SENSORS, DEFAULT_ENABLE_COMPLIANCE
            ),
        )
        current_fallback_to_closest = self.config_entry.options.get(
            CONF_FALLBACK_TO_CLOSEST,
            self.config_entry.data.get(
                CONF_FALLBACK_TO_CLOSEST, DEFAULT_FALLBACK_TO_CLOSEST
            ),
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
                vol.Required(
                    CONF_SCAN_INTERVAL,
                    default=OoklaSpeedtestConfigFlow._minutes_to_duration(
                        current_scan_interval
                    ),
                ): selector.DurationSelector(
                    selector.DurationSelectorConfig(enable_day=True)
                ),
                vol.Optional(
                    CONF_START_TIME,
                    description={"suggested_value": current_start_time},
                ): selector.TimeSelector(),
                vol.Optional(
                    CONF_ISP_DL_SPEED,
                    description={"suggested_value": current_isp_dl},
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_ISP_UL_SPEED,
                    description={"suggested_value": current_isp_ul},
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_ENABLE_LATENCY_SENSORS,
                    default=current_enable_latency,
                ): bool,
                vol.Optional(
                    CONF_ENABLE_COMPLIANCE_SENSORS,
                    default=current_enable_compliance,
                ): bool,
                vol.Optional(
                    CONF_FALLBACK_TO_CLOSEST,
                    default=current_fallback_to_closest,
                ): bool,
            }
        )

        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=schema,
                errors=errors,
            )

        # Process input
        scan_interval_input = user_input[CONF_SCAN_INTERVAL]
        if isinstance(scan_interval_input, dict):
            scan_interval = OoklaSpeedtestConfigFlow._duration_to_minutes(
                scan_interval_input
            )
        else:
            scan_interval = scan_interval_input

        start_time = user_input.get(CONF_START_TIME)

        # Validate time format
        if start_time and not validate_time_format(start_time):
            errors[CONF_START_TIME] = "Invalid time format"
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

        # Return options data
        return self.async_create_entry(
            title="",
            data={
                CONF_SERVER_ID: server_id,
                CONF_MANUAL: user_input[CONF_MANUAL],
                CONF_SCAN_INTERVAL: scan_interval,
                CONF_START_TIME: start_time,
                CONF_ISP_DL_SPEED: user_input.get(CONF_ISP_DL_SPEED),
                CONF_ISP_UL_SPEED: user_input.get(CONF_ISP_UL_SPEED),
                CONF_ENABLE_LATENCY_SENSORS: user_input.get(
                    CONF_ENABLE_LATENCY_SENSORS, DEFAULT_ENABLE_LATENCY
                ),
                CONF_ENABLE_COMPLIANCE_SENSORS: user_input.get(
                    CONF_ENABLE_COMPLIANCE_SENSORS, DEFAULT_ENABLE_COMPLIANCE
                ),
                CONF_FALLBACK_TO_CLOSEST: user_input.get(
                    CONF_FALLBACK_TO_CLOSEST, DEFAULT_FALLBACK_TO_CLOSEST
                ),
            },
        )
