"""Sensor platform for Fronius GEN24 Energy."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_PV_TOTAL,
    SENSOR_GRID_EXPORT,
    SENSOR_GRID_IMPORT,
)
from .coordinator import FroniusGen24EnergyCoordinator


@dataclass(frozen=True, kw_only=True)
class FroniusEnergySensorDescription(SensorEntityDescription):
    """Describes a Fronius GEN24 energy sensor."""
    data_key: str = ""


SENSOR_DESCRIPTIONS: tuple[FroniusEnergySensorDescription, ...] = (
    FroniusEnergySensorDescription(
        key=SENSOR_PV_TOTAL,
        data_key=SENSOR_PV_TOTAL,
        name="PV Gesamtproduktion",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        icon="mdi:solar-power",
        suggested_display_precision=0,
    ),
    FroniusEnergySensorDescription(
        key=SENSOR_GRID_EXPORT,
        data_key=SENSOR_GRID_EXPORT,
        name="Einspeisung ins Netz",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        icon="mdi:transmission-tower-export",
        suggested_display_precision=0,
    ),
    FroniusEnergySensorDescription(
        key=SENSOR_GRID_IMPORT,
        data_key=SENSOR_GRID_IMPORT,
        name="Netzbezug",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        icon="mdi:transmission-tower-import",
        suggested_display_precision=0,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Fronius GEN24 Energy sensors from a config entry."""
    coordinator: FroniusGen24EnergyCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        FroniusGen24EnergySensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class FroniusGen24EnergySensor(
    CoordinatorEntity[FroniusGen24EnergyCoordinator], SensorEntity
):
    """A single cumulative energy sensor backed by Modbus data."""

    entity_description: FroniusEnergySensorDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FroniusGen24EnergyCoordinator,
        entry: ConfigEntry,
        description: FroniusEnergySensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Fronius GEN24 Energy",
            "manufacturer": "Fronius",
            "model": "GEN24",
            "configuration_url": f"http://{entry.data['host']}",
        }

    @property
    def native_value(self) -> float | None:
        """Return the current sensor value in Wh."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)
