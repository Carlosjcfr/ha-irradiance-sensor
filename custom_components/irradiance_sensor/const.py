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
DEFAULT_REGISTERS = {
    "irradiance": {"addr": 0, "gain": 1.0, "offset": 0.0},
    "temp_ext": {"addr": 1, "gain": 0.1, "offset": 0.0},
    "temp_int": {"addr": 2, "gain": 0.1, "offset": 0.0},
    "wind_v": {"addr": 3, "gain": 0.1, "offset": 0.0},
    "wind_dir": {"addr": 4, "gain": 1.0, "offset": 0.0},
}