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
    MODEL_CUSTOM,
    DEFAULT_REGISTERS,
    MODEL_CUSTOM,
    DEFAULT_REGISTERS,
    SENSOR_TYPES,
    CONF_REGISTER_TYPE,
    CONF_ROW_UNIQUE_ID,
    REG_TYPE_HOLDING,
    REG_TYPE_INPUT,
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
        self._param_keys = []
        self._current_param_idx = 0
        self._collected_params = {}

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
                return await self.async_step_select_sensors()

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

    async def async_step_select_sensors(self, user_input=None):
        """Allow user to select which sensors to configure."""
        errors = {}
        
        # Load defaults based on selected model
        selected_model = self.data.get(CONF_SENSOR_MODEL)
        
        # Ensure templates are loaded
        if not self.loaded_templates:
            await self.hass.async_add_executor_job(self._load_templates)
            
        defaults = DEFAULT_REGISTERS
        if selected_model in self.loaded_templates:
            defaults = self.loaded_templates[selected_model]
            
        if user_input is not None:
            self._param_keys = user_input.get("selected_sensors", [])
            self._current_param_idx = 0
            self._collected_params = {}
            self._current_defaults = defaults
            
            # Pre-fill 'enabled' as True for all selected
            for k in self._param_keys:
                 self._collected_params[f"{k}_enabled"] = True
                 
            if not self._param_keys:
                return await self.async_step_final_config()
                
            return await self.async_step_configure_param()
            
        # Build options for selector
        available_keys = list(defaults.keys())
        options_list = []
        for key in available_keys:
            # Try to find friendly name
            name = key.replace("_", " ").title()
            if key in SENSOR_TYPES:
                name = SENSOR_TYPES[key].get("name", name)
            
            options_list.append({"value": key, "label": name})
            
        # Select all by default
        schema = vol.Schema({
            vol.Required("selected_sensors", default=available_keys): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options_list,
                    mode=selector.SelectSelectorMode.LIST,
                    multiple=True
                )
            )
        })

        return self.async_show_form(
            step_id="select_sensors", data_schema=schema, errors=errors
        )

    async def async_step_configure_param(self, user_input=None):
        """Handle configuration for a single parameter."""
        errors = {}
        
        # Check if we are done
        if self._current_param_idx >= len(self._param_keys):
            return await self.async_step_final_config()
            
        current_key = self._param_keys[self._current_param_idx]
        
        # Get default values for this key
        # We look in the loaded defaults first, then fallback to hardcoded DEFAULT_REGISTERS
        def_vals = DEFAULT_REGISTERS.get(current_key, {"addr": 0, "gain": 1.0, "offset": 0.0})
        # Always enable by default to ensure users see the sensor options checked
        is_enabled_default = True
        
        current_def = self._current_defaults.get(current_key, def_vals)
        
        if user_input is not None:
            # Save the collected input for this parameter
            self._collected_params[f"{current_key}_enabled"] = True
            self._collected_params[f"{current_key}_name"] = user_input.get("name")
            self._collected_params[f"{current_key}_{CONF_ROW_UNIQUE_ID}"] = user_input.get(CONF_ROW_UNIQUE_ID)
            self._collected_params[f"{current_key}_{CONF_REGISTER_TYPE}"] = user_input.get(CONF_REGISTER_TYPE)
            # Ensure address is int, others float
            self._collected_params[f"{current_key}_addr"] = int(user_input.get("addr"))
            self._collected_params[f"{current_key}_gain"] = float(user_input.get("gain"))
            self._collected_params[f"{current_key}_offset"] = float(user_input.get("offset"))
            
            # Next parameter
            self._current_param_idx += 1
            return await self.async_step_configure_param()

        # Build schema for this parameter using Selectors for better UI/Type handling
        schema_dict = {
            # Enabled field removed as selection happened in previous step
            vol.Optional("name", default=current_key.replace("_", " ").title()): selector.TextSelector(),
            vol.Optional(CONF_ROW_UNIQUE_ID, default=current_def.get("unique_id", f"{current_key}_modbus")): selector.TextSelector(),
            vol.Optional(CONF_REGISTER_TYPE, default=current_def.get("type", REG_TYPE_INPUT)): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"label": "Input Register (04)", "value": REG_TYPE_INPUT},
                        {"label": "Holding Register (03)", "value": REG_TYPE_HOLDING},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional("addr", default=current_def.get("addr", 0)): selector.NumberSelector(
                selector.NumberSelectorConfig(min=0, max=65535, mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional("gain", default=current_def.get("gain", 1.0)): selector.NumberSelector(
                selector.NumberSelectorConfig(step="any", mode=selector.NumberSelectorMode.BOX)
            ),
            vol.Optional("offset", default=current_def.get("offset", 0.0)): selector.NumberSelector(
                selector.NumberSelectorConfig(step="any", mode=selector.NumberSelectorMode.BOX)
            ),
        }

        return self.async_show_form(
            step_id="configure_param",
            data_schema=vol.Schema(schema_dict),
            description_placeholders={"param_name": current_key.replace("_", " ").title()},
            errors=errors
        )

    async def async_step_final_config(self, user_input=None):
        """Final step to set entity name and save template."""
        errors = {}
        
        if user_input is not None:
            # Handle saving template if requested
            if user_input.get("save_as_template") and user_input.get(CONF_TEMPLATE_NAME):
                new_regs = {}
                for key in self._param_keys:
                    # Only save to template if enabled
                    if self._collected_params.get(f"{key}_enabled", True):
                        new_regs[key] = {
                            "addr": self._collected_params.get(f"{key}_addr"),
                            "gain": self._collected_params.get(f"{key}_gain"),
                            "offset": self._collected_params.get(f"{key}_offset"),
                            "type": self._collected_params.get(f"{key}_{CONF_REGISTER_TYPE}"),
                            "unique_id": self._collected_params.get(f"{key}_{CONF_ROW_UNIQUE_ID}")
                        }
                
                await self.hass.async_add_executor_job(
                    self._save_template, 
                    user_input.get(CONF_TEMPLATE_NAME), 
                    new_regs
                )

            # Merge all data
            final_data = {**self.data, **self._collected_params, **user_input}
            return self.async_create_entry(
                title=final_data.get(CONF_ENTITY_NAME, "Irradiance Sensor"), 
                data=final_data
            )

        # Schema for final options
        schema_dict = {
            vol.Optional(CONF_ENTITY_NAME, default=self.data.get(CONF_SENSOR_MODEL, "Irradiance Sensor")): str,
            vol.Optional("save_as_template", default=False): bool,
            vol.Optional(CONF_TEMPLATE_NAME): str,
        }

        return self.async_show_form(
            step_id="final_config", 
            data_schema=vol.Schema(schema_dict), 
            errors=errors
        )
