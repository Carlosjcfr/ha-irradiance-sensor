"""Config flow for Irradiance Sensor integration."""
import logging
import voluptuous as vol
import json
import os
import ipaddress
import serial.tools.list_ports

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_CONNECTION_METHOD,
    CONF_IP_ADDRESS,
    CONF_PORT,
    CONF_SERIAL_PORT,
    CONF_BAUDRATE,
    CONF_MODBUS_ID,
    CONF_SENSOR_MODEL,
    CONF_TEMPLATE_NAME,
    CONF_ENTITY_NAME,
    METHOD_MODBUS_TCP,
    METHOD_RS485,
    MODEL_CUSTOM,
    DEFAULT_REGISTERS,
)

_LOGGER = logging.getLogger(__name__)

class IrradianceSensorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Irradiance Sensor."""

    VERSION = 1

    def __init__(self):
        """Initialize."""
        self.data = {}
        self.templates = []
        self.loaded_templates = {}
        self.selected_method = None

    def _get_templates_path(self):
        """Get path to templates.json."""
        # For this environment, we use the relative path to where the file is.
        return os.path.join(os.path.dirname(__file__), "templates.json")

    def _load_templates(self):
        """Load templates from JSON."""
        path = self._get_templates_path()
        try:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = json.load(f)
                    self.templates = []
                    self.loaded_templates = {}
                    for item in data:
                        name = item.get("name")
                        if name:
                            self.templates.append(name)
                            self.loaded_templates[name] = item.get("registers", {})
            else:
                 self.templates = ["Generic Irradiance"]
        except Exception as e:
            _LOGGER.error(f"Error loading templates: {e}")
            self.templates = ["Generic Irradiance"]

    def _get_serial_ports(self):
        """Get list of system serial ports."""
        try:
            return [p.device for p in serial.tools.list_ports.comports()]
        except Exception as e:
            _LOGGER.error(f"Error listing serial ports: {e}")
            return []

    async def async_step_user(self, user_input=None):
        """Handle the initial step (Connection Method Selection)."""
        errors = {}
        
        if user_input is not None:
            self.selected_method = user_input[CONF_CONNECTION_METHOD]
            self.data.update(user_input)
            return await self.async_step_setup_params()

        schema = vol.Schema({
            vol.Required(CONF_CONNECTION_METHOD, default=METHOD_MODBUS_TCP): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[METHOD_MODBUS_TCP, METHOD_RS485],
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )

    async def async_step_setup_params(self, user_input=None):
        """Handle the second step (Connection Details & Model)."""
        errors = {}
        
        # Load templates dynamically
        await self.hass.async_add_executor_job(self._load_templates)
        
        if user_input is not None:
            # Validate input based on method
            if self.selected_method == METHOD_MODBUS_TCP:
                ip_addr = user_input.get(CONF_IP_ADDRESS)
                try:
                    ipaddress.ip_address(ip_addr)
                except ValueError:
                    errors[CONF_IP_ADDRESS] = "invalid_ip"
                
                port = user_input.get(CONF_PORT)
                if not (1 <= port <= 65535):
                     errors[CONF_PORT] = "invalid_port"

            elif self.selected_method == METHOD_RS485:
                 pass # Serial port selection is restricted by dropdown, baudrate by dropdown/int
            
            modbus_id = user_input.get(CONF_MODBUS_ID)
            if not (1 <= modbus_id <= 247):
                 errors[CONF_MODBUS_ID] = "invalid_modbus_id"

            if not errors:
                self.data.update(user_input)
                return await self.async_step_mapping()

        # Build schema dynamically
        schema_dict = {}

        if self.selected_method == METHOD_MODBUS_TCP:
            schema_dict[vol.Required(CONF_IP_ADDRESS)] = str
            schema_dict[vol.Required(CONF_PORT, default=502)] = int
            schema_dict[vol.Required(CONF_MODBUS_ID, default=1)] = int

        elif self.selected_method == METHOD_RS485:
            # Get ports
            ports = await self.hass.async_add_executor_job(self._get_serial_ports)
            if not ports:
                ports = ["/dev/ttyUSB0", "/dev/ttyS0"] # Fallback manual entry or hint

            schema_dict[vol.Required(CONF_SERIAL_PORT)] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=ports,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                    custom_value=True # Allow custom if not found
                )
            )
            schema_dict[vol.Required(CONF_BAUDRATE, default=9600)] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=["9600", "14400", "19200", "38400", "57600", "115200"],
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            )
            schema_dict[vol.Required(CONF_MODBUS_ID, default=1)] = int

        # Common Sensor Model Selection
        # Ensure we have at least one template, defaulting to Generic if list empty (though handled in _load mostly)
        default_model = self.templates[0] if self.templates else "Generic Irradiance"
        
        schema_dict[vol.Required(CONF_SENSOR_MODEL, default=default_model)] = selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=self.templates,
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            )

        return self.async_show_form(
            step_id="setup_params", data_schema=vol.Schema(schema_dict), errors=errors
        )

    def _save_template(self, name, registers):
        """Save a new template to JSON."""
        path = self._get_templates_path()
        try:
            current_data = []
            if os.path.exists(path):
                with open(path, 'r') as f:
                    current_data = json.load(f)
            
            # Check if exists and update, or append
            found = False
            for item in current_data:
                if item.get("name") == name:
                    item["registers"] = registers
                    found = True
                    break
            if not found:
                current_data.append({"name": name, "registers": registers})
                
            with open(path, 'w') as f:
                json.dump(current_data, f, indent=2)
                
        except Exception as e:
            _LOGGER.error(f"Error saving template: {e}")

    async def async_step_mapping(self, user_input=None):
        """Handle the third step (Mapping Registers)."""
        errors = {}

        if user_input is not None:
             # Handle saving template
            if user_input.get("save_as_template") and user_input.get(CONF_TEMPLATE_NAME):
                 # Construct registers dict from input
                new_regs = {}
                for key in DEFAULT_REGISTERS:
                    new_regs[key] = {
                        "addr": user_input.get(f"{key}_addr"),
                        "gain": user_input.get(f"{key}_gain"),
                        "offset": user_input.get(f"{key}_offset")
                    }
                
                await self.hass.async_add_executor_job(
                    self._save_template, 
                    user_input.get(CONF_TEMPLATE_NAME), 
                    new_regs
                )

            final_data = {**self.data, **user_input}
            return self.async_create_entry(
                title=final_data.get(CONF_ENTITY_NAME, "Irradiance Sensor"), 
                data=final_data
            )

        # Pre-fill defaults
        selected_model = self.data.get(CONF_SENSOR_MODEL)
        
        # Determine defaults to show
        defaults = DEFAULT_REGISTERS
        
        if selected_model in self.loaded_templates:
            defaults = self.loaded_templates[selected_model]
        else:
            await self.hass.async_add_executor_job(self._load_templates)
            if selected_model in self.loaded_templates:
                defaults = self.loaded_templates[selected_model]

        schema_dict = {}
        entity_name_default = selected_model
        schema_dict[vol.Required(CONF_ENTITY_NAME, default=entity_name_default)] = str

        for key, def_vals in DEFAULT_REGISTERS.items():
            current_def = defaults.get(key, def_vals)
            
            schema_dict[vol.Required(f"{key}_addr", default=current_def.get("addr", def_vals["addr"]))] = int
            schema_dict[vol.Required(f"{key}_gain", default=current_def.get("gain", def_vals["gain"]))] = float
            schema_dict[vol.Required(f"{key}_offset", default=current_def.get("offset", def_vals["offset"]))] = float

        schema_dict[vol.Optional("save_as_template", default=False)] = bool
        schema_dict[vol.Optional(CONF_TEMPLATE_NAME)] = str

        return self.async_show_form(
            step_id="mapping", 
            data_schema=vol.Schema(schema_dict), 
            errors=errors
        )
