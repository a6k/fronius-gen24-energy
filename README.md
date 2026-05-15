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

These three lifetime counters are provided by the integration:

| Entity | Description | Unit |
|---|---|---|
| `sensor.fronius_gen24_energy_pv_gesamtproduktion` | Total PV energy produced (lifetime) | Wh |
| `sensor.fronius_gen24_energy_einspeisung_ins_netz` | Total energy exported to grid (lifetime) | Wh |
| `sensor.fronius_gen24_energy_netzbezug` | Total energy imported from grid (lifetime) | Wh |

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

## HA Configuration: utility_meter, template sensors, Energy Dashboard

The file [`ha_config/fronius_energy.yaml`](ha_config/fronius_energy.yaml) is a ready-to-use HA package that adds:

- **9 utility_meter sensors** — daily, monthly, and yearly deltas for PV production, grid export, and grid import
- **6 template sensors** — Eigenverbrauch, Autarkie (%), and Eigenverbrauchsquote (%) for today and the current month

### One-shot setup (run in HA terminal)

```bash
curl -fsSL https://raw.githubusercontent.com/a6k/fronius-gen24-energy/main/ha_config/setup.sh | bash
ha core restart
```

The script creates `/config/packages/fronius_energy.yaml` and patches `configuration.yaml` to include the packages directory.

### Resulting sensors

After restart, the following sensors are available:

| Entity | Description | Unit |
|---|---|---|
| `sensor.pv_energie_tag` | PV production today | Wh |
| `sensor.pv_energie_monat` | PV production this month | Wh |
| `sensor.pv_energie_jahr` | PV production this year | Wh |
| `sensor.einspeisung_tag` | Grid export today | Wh |
| `sensor.einspeisung_monat` | Grid export this month | Wh |
| `sensor.einspeisung_jahr` | Grid export this year | Wh |
| `sensor.netzbezug_tag` | Grid import today | Wh |
| `sensor.netzbezug_monat` | Grid import this month | Wh |
| `sensor.netzbezug_jahr` | Grid import this year | Wh |
| `sensor.eigenverbrauch_heute` | Self-consumption today (PV − export) | Wh |
| `sensor.eigenverbrauch_monat` | Self-consumption this month | Wh |
| `sensor.autarkie_heute` | Self-sufficiency today | % |
| `sensor.autarkie_monat` | Self-sufficiency this month | % |
| `sensor.eigenverbrauchsquote_heute` | Self-consumption ratio today | % |
| `sensor.eigenverbrauchsquote_monat` | Self-consumption ratio this month | % |

### Formulas

```
Eigenverbrauch      = PV − Einspeisung
Autarkie            = Eigenverbrauch / (Eigenverbrauch + Netzbezug) × 100
Eigenverbrauchsquote = Eigenverbrauch / PV × 100
```

### Energy Dashboard

Configure via **Settings → Energy**:

| Field | Sensor |
|---|---|
| Solar energy | `sensor.fronius_gen24_energy_pv_gesamtproduktion` |
| Grid consumption | `sensor.fronius_gen24_energy_netzbezug` |
| Grid return | `sensor.fronius_gen24_energy_einspeisung_ins_netz` |

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
