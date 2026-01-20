"""Constants for the Irradiance Sensor integration."""

DOMAIN = "irradiance_sensor"

CONF_CONNECTION_METHOD = "connection_method"
CONF_IP_ADDRESS = "ip_address"
CONF_PORT = "port"
CONF_SERIAL_PORT = "serial_port"
CONF_BAUDRATE = "baudrate"
CONF_MODBUS_ID = "modbus_id"
CONF_SENSOR_MODEL = "sensor_model"
CONF_SAVE_TEMPLATE = "save_template"
CONF_TEMPLATE_NAME = "template_name"
CONF_ENTITY_NAME = "entity_name"

METHOD_MODBUS_TCP = "Modbus TCP"
METHOD_RS485 = "RS485"

MODEL_CUSTOM = "Añadir personalizado"
MODEL_GENERIC = "Generic Irradiance"

# Default registers configuration (Address, Gain, Offset)

# Sensor Definitions with defaults and metadata
SENSOR_TYPES = {
    "irradiance": {
        "name": "Irradiance",
        "unit": "W/m²",
        "device_class": "irradiance",
        "default_addr": 0,
        "default_gain": 1.0,
        "default_offset": 0.0,
    },
    "temp_ext": {
        "name": "External Temperature",
        "unit": "°C",
        "device_class": "temperature",
        "default_addr": 1,
        "default_gain": 0.1,
        "default_offset": 0.0,
    },
    "temp_int": {
        "name": "Internal Temperature",
        "unit": "°C",
        "device_class": "temperature",
        "default_addr": 2,
        "default_gain": 0.1,
        "default_offset": 0.0,
    },
    "wind_v": {
        "name": "Wind Speed",
        "unit": "m/s",
        "device_class": "wind_speed",
        "default_addr": 3,
        "default_gain": 0.1,
        "default_offset": 0.0,
    },
    "wind_dir": {
        "name": "Wind Direction",
        "unit": "°",
        "device_class": None, # None for wind direction usually, or specific if available
        "default_addr": 4,
        "default_gain": 1.0,
        "default_offset": 0.0,
    },
}

# Values for compatibility
DEFAULT_REGISTERS = {
    k: {
        "addr": v["default_addr"], 
        "gain": v["default_gain"], 
        "offset": v["default_offset"]
    }
    for k, v in SENSOR_TYPES.items()
}