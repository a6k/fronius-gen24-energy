"""DataUpdateCoordinator for Fronius GEN24 Energy."""
from __future__ import annotations

import logging
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    UNIT_INVERTER,
    UNIT_METER,
    REG_INV_PV_ENERGY_HI,
    REG_METER_EXPORT_HI,
    REG_METER_IMPORT_HI,
    REG_METER_ENERGY_SF,
    SENSOR_PV_TOTAL,
    SENSOR_GRID_EXPORT,
    SENSOR_GRID_IMPORT,
)

_LOGGER = logging.getLogger(__name__)


def _acc32(hi: int, lo: int) -> int:
    """Combine two uint16 registers into a single uint32 (acc32)."""
    return (hi << 16) | lo


def _int16(val: int) -> int:
    """Convert uint16 Modbus register value to signed int16."""
    return val if val < 32768 else val - 65536


def _apply_sf(raw: int, sf: int) -> float:
    """Apply SunSpec scale factor: result = raw × 10^sf."""
    return raw * (10 ** sf)


class FroniusGen24EnergyCoordinator(DataUpdateCoordinator[dict[str, float]]):
    """Reads cumulative energy registers from Fronius GEN24 via Modbus TCP."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        port: int,
        scan_interval: int,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._host = host
        self._port = port

    async def _async_update_data(self) -> dict[str, float]:
        """Fetch energy data from inverter and smart meter."""
        client = AsyncModbusTcpClient(self._host, port=self._port)
        try:
            await client.connect()
            if not client.connected:
                raise UpdateFailed(f"Cannot connect to {self._host}:{self._port}")

            # --- Inverter: PV total energy (Unit 1) ---
            r = await client.read_holding_registers(
                REG_INV_PV_ENERGY_HI, 2, UNIT_INVERTER
            )
            if r.isError():
                raise UpdateFailed(f"Modbus error reading inverter energy: {r}")
            pv_total_wh = float(_acc32(r.registers[0], r.registers[1]))

            # --- Smart Meter: scale factor (Unit 200) ---
            r = await client.read_holding_registers(
                REG_METER_ENERGY_SF, 1, UNIT_METER
            )
            if r.isError():
                raise UpdateFailed(f"Modbus error reading meter SF: {r}")
            meter_sf = _int16(r.registers[0])

            # --- Smart Meter: grid export (Unit 200) ---
            r = await client.read_holding_registers(
                REG_METER_EXPORT_HI, 2, UNIT_METER
            )
            if r.isError():
                raise UpdateFailed(f"Modbus error reading meter export: {r}")
            export_wh = _apply_sf(_acc32(r.registers[0], r.registers[1]), meter_sf)

            # --- Smart Meter: grid import (Unit 200) ---
            r = await client.read_holding_registers(
                REG_METER_IMPORT_HI, 2, UNIT_METER
            )
            if r.isError():
                raise UpdateFailed(f"Modbus error reading meter import: {r}")
            import_wh = _apply_sf(_acc32(r.registers[0], r.registers[1]), meter_sf)

        except ModbusException as exc:
            raise UpdateFailed(f"Modbus communication error: {exc}") from exc
        finally:
            client.close()

        _LOGGER.debug(
            "Fronius GEN24 energy: PV=%.0f Wh, export=%.0f Wh, import=%.0f Wh",
            pv_total_wh,
            export_wh,
            import_wh,
        )

        return {
            SENSOR_PV_TOTAL: pv_total_wh,
            SENSOR_GRID_EXPORT: export_wh,
            SENSOR_GRID_IMPORT: import_wh,
        }
