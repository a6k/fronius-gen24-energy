# fronius-gen24-energy

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Home Assistant custom integration for **gap-free energy metering** on Fronius Symo GEN24 inverters via **Modbus TCP**.

## Problem

The official Fronius HA integration uses HTTP polling. Any interruption (HA restart, network hiccup) means lost Wh that can never be recovered — resulting in ~5–10% lower monthly values compared to Fronius Solar.web or the Fronius app.

## Solution

This integration reads **cumulative energy registers directly from the inverter and smart meter via Modbus TCP**. The inverter maintains its own counters independently of HA. After an HA restart, the integration picks up exactly where the inverter is — no data loss.

## Supported hardware

| Device | Model | Firmware |
|---|---|---|
| Inverter | Fronius Symo GEN24 (any size) | ≥ 1.34.6 |
| Smart Meter | Fronius Smart Meter TS 65A-3 | — |

## Sensors

| Entity | Description | Unit |
|---|---|---|
| `sensor.pv_gesamtproduktion` | Total PV energy produced (lifetime) | Wh |
| `sensor.einspeisung_ins_netz` | Total energy exported to grid (lifetime) | Wh |
| `sensor.netzbezug` | Total energy imported from grid (lifetime) | Wh |

All sensors have `state_class: total_increasing` and are compatible with the HA Energy Dashboard and `utility_meter`.

**Verified values (Fronius Symo GEN24 8.0, 2026-05-15):**
- PV Gesamtproduktion: 23.112.071 Wh
- Einspeisung ins Netz: 13.815.307 Wh
- Netzbezug: 3.879.792 Wh

## Prerequisites

1. Fronius GEN24 inverter on your local network
2. Modbus TCP enabled on the inverter:
   - Open `http://<inverter-ip>` → Communication → Modbus
   - Set **Mode: TCP Server**, Port: 502
   - Enable **Steuerung erlauben** (Control enable)

## Installation

### Via HACS (recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add `https://github.com/a6k/fronius-gen24-energy` → Category: Integration
3. Download → Restart HA

### Manual

Copy `custom_components/fronius_gen24_energy/` into your HA `config/custom_components/` folder and restart.

## Setup

Settings → Devices & Services → Add Integration → **Fronius GEN24 Energy**

Enter:
- **IP address** of your inverter (e.g. `10.0.0.200`)
- **Port**: `502`
- **Poll interval**: `10` seconds (recommended)

## Daily / monthly values with utility_meter

Add to `configuration.yaml`:

```yaml
utility_meter:
  pv_energie_tag:
    source: sensor.pv_gesamtproduktion
    cycle: daily
  pv_energie_monat:
    source: sensor.pv_gesamtproduktion
    cycle: monthly
  einspeisung_tag:
    source: sensor.einspeisung_ins_netz
    cycle: daily
  netzbezug_tag:
    source: sensor.netzbezug
    cycle: daily
```

## Modbus register reference

Verified against Fronius Symo GEN24 8.0, firmware 1.8.2, 2026-05-15.

> **Note on addressing:** Fronius GEN24 uses the full `4xxxx` register number directly as the Modbus PDU address (e.g. register 40188 in the docs → PDU address 40188). No offset subtraction needed.

| Sensor | Unit ID | Register (PDU addr) | Type | Scale Factor |
|---|---|---|---|---|
| PV total energy | 1 | 40188–40189 | acc32 | — (direct Wh) |
| Grid export | 200 | 40107–40108 | acc32 | reg 40123 |
| Grid import | 200 | 40115–40116 | acc32 | reg 40123 |
| Energy SF | 200 | 40123 | int16 | — (value: −2) |

## Compatibility

| Component | Version | Notes |
|---|---|---|
| Home Assistant | ≥ 2024.1 | Tested on 2026.5.x |
| pymodbus | 3.11.2 | Bundled with HA — do **not** declare in `requirements` |
| Python | 3.12 | |

**pymodbus API note:** This integration detects the correct slave/unit parameter name at runtime (`device_id` in pymodbus 3.11+, `slave` in earlier 3.x). No manual configuration needed.

## Roadmap

- [ ] Battery charged / discharged energy (Phase 2)
- [ ] Configurable meter unit ID (for non-standard setups)
- [ ] HACS default repository submission (Phase 3)

## License

MIT
