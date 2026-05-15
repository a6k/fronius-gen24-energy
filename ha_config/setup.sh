#!/usr/bin/env bash
# ============================================================
# Fronius GEN24 Energy — HA Setup-Skript
# Im HA Web-Terminal ausführen:
#   bash /config/fronius_setup.sh
# Oder als One-Liner:
#   curl -sL <url> | bash
# ============================================================
set -e

CONFIG=/config

echo "=== Fronius GEN24 Energy Setup ==="

# 1. Packages-Verzeichnis anlegen
mkdir -p "$CONFIG/packages"
echo "[1/4] Packages-Verzeichnis: OK"

# 2. Fronius Energy Package erstellen
cat > "$CONFIG/packages/fronius_energy.yaml" << 'YAML'
# ============================================================
# Fronius GEN24 Energy — HA Package
# Automatisch erstellt von fronius-gen24-energy Setup
# ============================================================

utility_meter:

  pv_energie_tag:
    source: sensor.fronius_gen24_energy_pv_gesamtproduktion
    cycle: daily
    unique_id: pv_energie_tag

  pv_energie_monat:
    source: sensor.fronius_gen24_energy_pv_gesamtproduktion
    cycle: monthly
    unique_id: pv_energie_monat

  pv_energie_jahr:
    source: sensor.fronius_gen24_energy_pv_gesamtproduktion
    cycle: yearly
    unique_id: pv_energie_jahr

  einspeisung_tag:
    source: sensor.fronius_gen24_energy_einspeisung_ins_netz
    cycle: daily
    unique_id: einspeisung_tag

  einspeisung_monat:
    source: sensor.fronius_gen24_energy_einspeisung_ins_netz
    cycle: monthly
    unique_id: einspeisung_monat

  einspeisung_jahr:
    source: sensor.fronius_gen24_energy_einspeisung_ins_netz
    cycle: yearly
    unique_id: einspeisung_jahr

  netzbezug_tag:
    source: sensor.fronius_gen24_energy_netzbezug
    cycle: daily
    unique_id: netzbezug_tag

  netzbezug_monat:
    source: sensor.fronius_gen24_energy_netzbezug
    cycle: monthly
    unique_id: netzbezug_monat

  netzbezug_jahr:
    source: sensor.fronius_gen24_energy_netzbezug
    cycle: yearly
    unique_id: netzbezug_jahr

template:
  - sensor:

      - name: "Eigenverbrauch Heute"
        unique_id: eigenverbrauch_heute
        unit_of_measurement: "Wh"
        device_class: energy
        state_class: total_increasing
        icon: mdi:home-lightning-bolt
        state: >
          {% set pv   = states('sensor.pv_energie_tag') | float(0) %}
          {% set feed = states('sensor.einspeisung_tag') | float(0) %}
          {{ [pv - feed, 0] | max | round(0) }}

      - name: "Autarkie Heute"
        unique_id: autarkie_heute
        unit_of_measurement: "%"
        icon: mdi:solar-power-variant
        state: >
          {% set pv      = states('sensor.pv_energie_tag') | float(0) %}
          {% set feed    = states('sensor.einspeisung_tag') | float(0) %}
          {% set grid    = states('sensor.netzbezug_tag') | float(0) %}
          {% set eigen   = [pv - feed, 0] | max %}
          {% set gesamt  = eigen + grid %}
          {% if gesamt > 0 %}
            {{ (eigen / gesamt * 100) | round(1) }}
          {% else %}
            0
          {% endif %}

      - name: "Eigenverbrauchsquote Heute"
        unique_id: eigenverbrauchsquote_heute
        unit_of_measurement: "%"
        icon: mdi:percent
        state: >
          {% set pv   = states('sensor.pv_energie_tag') | float(0) %}
          {% set feed = states('sensor.einspeisung_tag') | float(0) %}
          {% set eigen = [pv - feed, 0] | max %}
          {% if pv > 0 %}
            {{ (eigen / pv * 100) | round(1) }}
          {% else %}
            0
          {% endif %}

      - name: "Eigenverbrauch Monat"
        unique_id: eigenverbrauch_monat
        unit_of_measurement: "Wh"
        device_class: energy
        state_class: total_increasing
        icon: mdi:home-lightning-bolt
        state: >
          {% set pv   = states('sensor.pv_energie_monat') | float(0) %}
          {% set feed = states('sensor.einspeisung_monat') | float(0) %}
          {{ [pv - feed, 0] | max | round(0) }}

      - name: "Autarkie Monat"
        unique_id: autarkie_monat
        unit_of_measurement: "%"
        icon: mdi:solar-power-variant
        state: >
          {% set pv      = states('sensor.pv_energie_monat') | float(0) %}
          {% set feed    = states('sensor.einspeisung_monat') | float(0) %}
          {% set grid    = states('sensor.netzbezug_monat') | float(0) %}
          {% set eigen   = [pv - feed, 0] | max %}
          {% set gesamt  = eigen + grid %}
          {% if gesamt > 0 %}
            {{ (eigen / gesamt * 100) | round(1) }}
          {% else %}
            0
          {% endif %}

      - name: "Eigenverbrauchsquote Monat"
        unique_id: eigenverbrauchsquote_monat
        unit_of_measurement: "%"
        icon: mdi:percent
        state: >
          {% set pv   = states('sensor.pv_energie_monat') | float(0) %}
          {% set feed = states('sensor.einspeisung_monat') | float(0) %}
          {% set eigen = [pv - feed, 0] | max %}
          {% if pv > 0 %}
            {{ (eigen / pv * 100) | round(1) }}
          {% else %}
            0
          {% endif %}
YAML

echo "[2/4] Package-Datei: OK"

# 3. configuration.yaml: packages eintragen (falls noch nicht vorhanden)
if ! grep -q "packages:" "$CONFIG/configuration.yaml" 2>/dev/null; then
    # Check if homeassistant: block exists
    if grep -q "^homeassistant:" "$CONFIG/configuration.yaml" 2>/dev/null; then
        # Add packages under existing homeassistant block
        sed -i '/^homeassistant:/a\  packages: !include_dir_named packages' "$CONFIG/configuration.yaml"
    else
        # Add homeassistant block at top
        echo -e "homeassistant:\n  packages: !include_dir_named packages\n" | cat - "$CONFIG/configuration.yaml" > /tmp/ha_cfg_tmp && mv /tmp/ha_cfg_tmp "$CONFIG/configuration.yaml"
    fi
    echo "[3/4] configuration.yaml: packages hinzugefuegt"
else
    echo "[3/4] configuration.yaml: packages bereits vorhanden"
fi

# 4. Config validieren
echo "[4/4] Config-Check..."
ha core check 2>/dev/null || echo "   (ha CLI nicht verfuegbar - manuell pruefen)"

echo ""
echo "=== Setup abgeschlossen! ==="
echo ""
echo "Naechste Schritte:"
echo "  1. HA neu starten: ha core restart"
echo "  2. Energy Dashboard konfigurieren:"
echo "     Einstellungen -> Energie -> Strom-Netz"
echo "     + sensor.fronius_gen24_energy_netzbezug (Bezug)"
echo "     + sensor.fronius_gen24_energy_einspeisung_ins_netz (Einspeisung)"
echo "     Solarenergie: sensor.fronius_gen24_energy_pv_gesamtproduktion"
echo ""
echo "Neue Sensoren (nach Neustart):"
echo "  sensor.pv_energie_tag / _monat / _jahr"
echo "  sensor.einspeisung_tag / _monat / _jahr"
echo "  sensor.netzbezug_tag / _monat / _jahr"
echo "  sensor.eigenverbrauch_heute / _monat"
echo "  sensor.autarkie_heute / _monat"
echo "  sensor.eigenverbrauchsquote_heute / _monat"
