"""Config flow for Fronius GEN24 Energy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL

from .const import (
    DOMAIN,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    UNIT_INVERTER,
    REG_INV_PV_ENERGY_HI,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): vol.All(
            int, vol.Range(min=5, max=60)
        ),
    }
)


async def _test_connection(host: str, port: int) -> str | None:
    """Try to read one register. Returns error string or None on success."""
    client = AsyncModbusTcpClient(host, port=port)
    try:
        await client.connect()
        if not client.connected:
            return "cannot_connect"
        result = await client.read_holding_registers(
            REG_INV_PV_ENERGY_HI, count=2, slave=UNIT_INVERTER
        )
        if result.isError():
            return "modbus_error"
    except ModbusException:
        return "cannot_connect"
    except Exception:  # noqa: BLE001
        return "unknown"
    finally:
        client.close()
    return None


class FroniusGen24EnergyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the config flow for Fronius GEN24 Energy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            error = await _test_connection(host, port)
            if error:
                errors["base"] = error
            else:
                return self.async_create_entry(
                    title=f"Fronius GEN24 ({host})",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )
