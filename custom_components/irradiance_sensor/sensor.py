"""Platform for sensor integration."""
from __future__ import annotations

import logging
from datetime import timedelta
import asyncio

from pymodbus.client import ModbusTcpClient, ModbusSerialClient
from pymodbus.exceptions import ModbusException

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfIrradiance,
    UnitOfTemperature,
    UnitOfSpeed,
    DEGREE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN,
    DEFAULT_REGISTERS,
    SENSOR_TYPES,
    CONF_CONNECTION_METHOD,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_BAUDRATE,
    CONF_MODBUS_ID,
    CONF_SENSOR_MODEL,
    CONF_ENTITY_NAME,
    METHOD_MODBUS_TCP,
    METHOD_RS485,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Irradiance Sensor platform."""
    
    coordinator = IrradianceDataCoordinator(hass, entry.data)
    
    # Perform first refresh to sure we can connect
    await coordinator.async_config_entry_first_refresh()

    entities = []
    
    # Helper to create sensor
    def create_sensor(key, name, unit, device_class):
         return IrradianceSensorEntity(
            coordinator, 
            entry, 
            key, 
            name,
            unit,
            device_class
        )

    for key, type_def in SENSOR_TYPES.items():
        # Check if enabled (default to True for legacy configs)
        if not entry.data.get(f"{key}_enabled", True):
            continue
            
        entities.append(create_sensor(
            key, 
            type_def["name"], 
            type_def["unit"], 
            type_def["device_class"]
        ))

    async_add_entities(entities)


class IrradianceDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from Modbus."""

    def __init__(self, hass, config):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.config = config
        self.client = None
        self._connect_client()

    def _connect_client(self):
        """Initialize Modbus client."""
        method = self.config.get(CONF_CONNECTION_METHOD)
        
        if method == METHOD_MODBUS_TCP:
            host = self.config.get(CONF_IP_ADDRESS)
            port = self.config.get(CONF_PORT, 502)
            _LOGGER.debug(f"Initializing Modbus TCP Client: {host}:{port}")
            self.client = ModbusTcpClient(host=host, port=port)
            
        elif method == METHOD_RS485:
            port = self.config.get(CONF_SERIAL_PORT)
            baud = self.config.get(CONF_BAUDRATE, 9600)
            _LOGGER.debug(f"Initializing Modbus Serial Client: {port} @ {baud}")
            self.client = ModbusSerialClient(
                port=port,
                baudrate=baud,
                bytesize=8,
                parity='N',
                stopbits=1,
            )
    
    async def _async_update_data(self):
        """Fetch data from Modbus."""
        if not self.client:
            self._connect_client()
            
        if not self.client.connect():
             raise UpdateFailed(f"Could not connect to Modbus device ({self.config.get(CONF_CONNECTION_METHOD)})")
             
        data = {}
        slave_id = self.config.get(CONF_MODBUS_ID, 1) if self.config.get(CONF_CONNECTION_METHOD) == METHOD_RS485 else 1
        
        try:
             # Run sync modbus call in executor
            def read_modbus():
                results = {}
                # Collect addresses we need
                needed_addrs = []
                for key in SENSOR_TYPES:
                    # Skip if disabled
                    if not self.config.get(f"{key}_enabled", True):
                        continue
                        
                    addr = self.config.get(f"{key}_addr")
                    if addr is not None:
                        needed_addrs.append(addr)

                for addr in set(needed_addrs): # Use set to avoid duplicates if multiple sensors share addr
                    # Read 1 register
                    rr = self.client.read_holding_registers(address=addr, count=1, slave=slave_id)
                    if rr.isError():
                        _LOGGER.warning(f"Error reading address {addr}: {rr}")
                        results[addr] = None
                    else:
                        results[addr] = rr.registers[0]
                return results

            data = await self.hass.async_add_executor_job(read_modbus)
            
        except Exception as e:
            self.client.close()
            raise UpdateFailed(f"Modbus error: {e}")

        return data

class IrradianceSensorEntity(CoordinatorEntity, SensorEntity):
    """Representation of an Irradiance Sensor."""

    def __init__(self, coordinator, entry, key, name_suffix, unit, device_class):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._key = key
        
        entity_name_prefix = entry.data.get(CONF_ENTITY_NAME, entry.title)
        self._attr_name = f"{entity_name_prefix} {name_suffix}"
        
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = SensorStateClass.MEASUREMENT
        
        self._addr = entry.data.get(f"{key}_addr", 0)
        self._gain = entry.data.get(f"{key}_gain", 1.0)
        self._offset = entry.data.get(f"{key}_offset", 0.0)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._entry.data.get(CONF_ENTITY_NAME, "Irradiance Sensor"),
            manufacturer="Custom Integration",
            model=self._entry.data.get(CONF_SENSOR_MODEL, "Generic"),
            configuration_url=(
                f"http://{self._entry.data.get(CONF_IP_ADDRESS)}" 
                if self._entry.data.get(CONF_CONNECTION_METHOD) == METHOD_MODBUS_TCP 
                else None
            ),
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None
            
        raw_val = self.coordinator.data.get(self._addr)
        if raw_val is None:
            return None
            
        # Apply logic
        value = (float(raw_val) * self._gain) + self._offset
        return round(value, 2)