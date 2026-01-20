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
CONF_REGISTER_TYPE = "register_type"

REG_TYPE_HOLDING = "holding"
REG_TYPE_INPUT = "input"


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
        "default_gain": 0.1,
        "default_offset": 0.0,
        "default_type": REG_TYPE_INPUT,
    },
    "temp_pv": {
        "name": "PV Module Temperature",
        "unit": "°C",
        "device_class": "temperature",
        "default_addr": 7,
        "default_gain": 0.1,
        "default_offset": 0.0,
        "default_type": REG_TYPE_INPUT,
    },
    "temp_amb": {
        "name": "Ambient Temperature",
        "unit": "°C",
        "device_class": "temperature",
        "default_addr": 8,
        "default_gain": 0.1,
        "default_offset": 0.0,
        "default_type": REG_TYPE_INPUT,
    },
}

# Values for compatibility
DEFAULT_REGISTERS = {
    k: {
        "addr": v["default_addr"], 
        "gain": v["default_gain"], 
        "offset": v["default_offset"],
        "type": v["default_type"]
    }
    for k, v in SENSOR_TYPES.items()
}