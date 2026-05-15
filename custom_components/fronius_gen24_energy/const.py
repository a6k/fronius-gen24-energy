"""Constants for Fronius GEN24 Energy integration."""

DOMAIN = "fronius_gen24_energy"

# Config entry keys
CONF_HOST = "host"
CONF_PORT = "port"
CONF_SCAN_INTERVAL = "scan_interval"

# Defaults
DEFAULT_HOST = "192.168.1.1"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 10  # seconds

# Modbus Unit IDs
UNIT_INVERTER = 1
UNIT_METER = 200

# ---------------------------------------------------------------------------
# Inverter registers (Unit 1, SunSpec Model 122 — Measurements/Status)
# Fronius GEN24 uses the 4xxxx register number directly as the PDU address
# (no subtraction needed — the inverter accepts 40188 as PDU address 40188)
# ---------------------------------------------------------------------------

# PV total lifetime energy (acc32, 2 registers, unit: Wh)
# Verified via raw Modbus scan 2026-05-15: (0x0160<<16)|0xA96D = 23 112 kWh
REG_INV_PV_ENERGY_HI = 40188   # high word  (PDU address = doc register number)
REG_INV_PV_ENERGY_LO = 40189   # low word

# ---------------------------------------------------------------------------
# Smart Meter registers (Unit 200, SunSpec Model 203 — Three-Phase Meter)
# Same direct-addressing convention as inverter.
# ---------------------------------------------------------------------------

# Total exported energy — Einspeisung ins Netz (acc32, unit: see SF)
# Verified via raw scan: (0x5258<<16)|0x7C4C × 10⁻² = 13 813 kWh
REG_METER_EXPORT_HI = 40107    # high word
REG_METER_EXPORT_LO = 40108    # low word

# Total imported energy — Netzbezug (acc32, unit: see SF)
# Verified via raw scan: (0x1720<<16)|0x17C0 × 10⁻² = 3 879 kWh
REG_METER_IMPORT_HI = 40115    # high word
REG_METER_IMPORT_LO = 40116    # low word

# Energy scale factor — shared for export and import (int16)
# Verified via raw scan: 0xFFFE = -2  →  raw_value × 10⁻² = Wh
REG_METER_ENERGY_SF = 40123

# ---------------------------------------------------------------------------
# Sensor keys (used as entity unique_id suffix and coordinator data keys)
# ---------------------------------------------------------------------------
SENSOR_PV_TOTAL    = "pv_total_energy"
SENSOR_GRID_EXPORT = "grid_export_energy"
SENSOR_GRID_IMPORT = "grid_import_energy"
