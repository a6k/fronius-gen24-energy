# fronius-gen24-energy — Projektplan

## Problem

Die offizielle Fronius HA-Integration (und alle bekannten Alternativen) nutzen
HTTP-Polling gegen die lokale Solar API. Dabei entstehen Datenlücken: HA liefert
~8 % weniger als die Fronius App bzw. Solar.web, weil verpasste Pollingzyklen
(HA-Neustart, kurze Netzunterbrechung) unwiederbringlich verloren sind.

## Lösung

Direkte Modbus-TCP-Verbindung zum Wechselrichter. Der Wechselrichter führt
kumulative Energiezähler intern — unabhängig von HA. HA liest diese Zähler
sekündlich, berechnet daraus Tages- und Monatswerte via `utility_meter`.
Ein HA-Neustart verursacht keine Lücke, weil der Zähler im Wechselrichter
weiterläuft.

## Unterstützte Hardware (getestet)

| Gerät | Modell | Firmware |
|---|---|---|
| Wechselrichter | Fronius Symo GEN24 8.0 | ≥ 1.34.6 |
| Smart Meter | Fronius Smart Meter TS 65A-3 | — |
| Batterie | BYD Battery-Box Premium HV | — |

## Gefundene Modbus-Register

### Wechselrichter (Unit ID 1)

| Sensor | Register | Typ | SF | Wert (verifiziert) |
|---|---|---|---|---|
| PV Gesamtproduktion | 40188–40189 | acc32 | — | 23.109 kWh ✓ |

SunSpec-Block: Model 122 (Measurements/Status), Daten ab Register 40184.

### Smart Meter (Unit ID 200)

| Sensor | Register | Typ | SF-Register | Wert (verifiziert) |
|---|---|---|---|---|
| Einspeisung (Export) | 40107–40108 | acc32 | 40123 (= −2) | 13.814 kWh ✓ |
| Netzbezug (Import) | 40115–40116 | acc32 | 40123 (= −2) | 3.879 kWh ✓ |

SunSpec-Block: Model 203 (Three-Phase Meter), Daten ab Register 40072.

### Noch zu ermitteln

- Batterie geladen / entladen (vermutlich Model 124 oder 160, Unit 1)
- Wallbox-Energie (nicht über Modbus verfügbar → bleibt bei HTTP)

## Architektur (geplant)

```
Fronius GEN24
  └── Modbus TCP :502
        ├── Unit 1  (Wechselrichter)  → PV Produktion
        └── Unit 200 (Smart Meter)   → Einspeisung, Netzbezug

HA Custom Integration (HACS)
  ├── modbus_coordinator.py   — liest Register, cached Werte
  ├── sensor.py               — erstellt HA-Sensoren (total_increasing)
  ├── config_flow.py          — UI-Setup: IP-Adresse, Polling-Intervall
  └── utility_meter (auto)    — täglicher + monatlicher Reset
```

## Abgrenzung zu bestehenden Projekten

| Projekt | Fokus | Energie-Genauigkeit |
|---|---|---|
| HA Fronius (offiziell) | Echtzeit, Solar API HTTP | Lücken möglich |
| fronius_modbus (redpomodoro) | Batterie-Steuerung | nicht im Fokus |
| fronius_modbus (callifo) | Batterie-Steuerung | nicht im Fokus |
| **fronius-gen24-energy** | **Lückenlose Energiemessung** | **Ziel: = Solar.web** |

## Entwicklungsphasen

### Phase 1 — Grundgerüst (MVP)
- [ ] HACS-kompatible Ordnerstruktur anlegen
- [ ] `config_flow.py`: IP-Eingabe, Verbindungstest
- [ ] `modbus_coordinator.py`: Register lesen, Fehlerbehandlung
- [ ] `sensor.py`: PV Produktion, Einspeisung, Netzbezug als `total_increasing`
- [ ] `manifest.json`, `strings.json`, Übersetzungen (DE/EN)
- [ ] README mit Setup-Anleitung

### Phase 2 — Batterie & Erweiterung
- [ ] Batterie-Register ermitteln (Model 124/160)
- [ ] Batterie geladen/entladen als Sensoren
- [ ] Konfigurierbares Polling-Intervall (Standard: 10s)

### Phase 3 — Qualität & Community
- [ ] Unit Tests
- [ ] GitHub Actions CI
- [ ] HACS Default Repository Antrag
- [ ] Dokumentation: unterstützte Firmware-Versionen

## Offene Fragen

1. Skalierungsfaktor PV-Register 40188: ist er immer 1 (= direkt in Wh) oder
   gibt es eine SF-Register-Referenz?
2. Verhält sich Unit ID bei mehreren Wechselrichtern (Multi-Inverter)?
3. Welche Mindest-Firmware ist für alle gefundenen Register erforderlich?
