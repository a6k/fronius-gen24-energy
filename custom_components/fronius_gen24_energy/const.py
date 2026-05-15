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
# Model 122 header at 40182–40183, data starts at 40184 (1-indexed)
# pymodbus uses 0-based addressing → subtract 1
# ---------------------------------------------------------------------------

# PV total lifetime energy (acc32, 2 registers, unit: Wh)
# Verified: matches HTTP API E_Total (23 109 kWh @ 2026-05-15)
REG_INV_PV_ENERGY_HI = 40187   # high word  (register 40188 in docs)
REG_INV_PV_ENERGY_LO = 40188   # low word   (register 40189 in docs)

# ---------------------------------------------------------------------------
# Smart Meter registers (Unit 200, SunSpec Model 203 — Three-Phase Meter)
# Model 203 header at 40070–40071, data starts at 40072 (1-indexed)
# ---------------------------------------------------------------------------

# Total exported energy — Einspeisung ins Netz (acc32, unit: see SF)
# Verified: 13 814 kWh @ 2026-05-15
REG_METER_EXPORT_HI = 40106    # high word  (register 40107 in docs)
REG_METER_EXPORT_LO = 40107    # low word   (register 40108 in docs)

# Total imported energy — Netzbezug (acc32, unit: see SF)
# Verified: 3 879 kWh @ 2026-05-15
REG_METER_IMPORT_HI = 40114    # high word  (register 40115 in docs)
REG_METER_IMPORT_LO = 40115    # low word   (register 40116 in docs)

# Energy scale factor — shared for export and import (int16)
# Verified: -2  →  raw_value × 10⁻² = Wh
REG_METER_ENERGY_SF = 40122    # (register 40123 in docs)

# ---------------------------------------------------------------------------
# Sensor keys (used as entity unique_id suffix and coordinator data keys)
# ---------------------------------------------------------------------------
SENSOR_PV_TOTAL    = "pv_total_energy"
SENSOR_GRID_EXPORT = "grid_export_energy"
SENSOR_GRID_IMPORT = "grid_import_energy"
