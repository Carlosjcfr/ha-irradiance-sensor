"""Config flow for Irradiance Sensor integration."""
import logging
import voluptuous as vol
import json
import os

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
                    self.templates = [MODEL_CUSTOM]
                    self.loaded_templates = {}
                    for item in data:
                        name = item.get("name")
                        if name:
                            self.templates.append(name)
                            self.loaded_templates[name] = item.get("registers", {})
            else:
                 self.templates = [MODEL_CUSTOM, "Generic Irradiance"]
        except Exception as e:
            _LOGGER.error(f"Error loading templates: {e}")
            self.templates = [MODEL_CUSTOM, "Generic Irradiance"]

    async def async_step_user(self, user_input=None):
        """Handle the initial step (Connection)."""
        errors = {}
        
        # Load templates dynamically
        await self.hass.async_add_executor_job(self._load_templates)
        
        if user_input is not None:
            method = user_input.get(CONF_CONNECTION_METHOD)
            if method == METHOD_MODBUS_TCP:
                if not user_input.get(CONF_IP_ADDRESS):
                    errors[CONF_IP_ADDRESS] = "required"
            elif method == METHOD_RS485:
                if not user_input.get(CONF_SERIAL_PORT):
                     errors[CONF_SERIAL_PORT] = "required"

            if not errors:
                self.data.update(user_input)
                return await self.async_step_mapping()

        schema = vol.Schema({
            vol.Required(CONF_CONNECTION_METHOD, default=METHOD_MODBUS_TCP): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[METHOD_MODBUS_TCP, METHOD_RS485],
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Optional(CONF_IP_ADDRESS): str,
            vol.Optional(CONF_PORT, default=502): int,
            vol.Optional(CONF_SERIAL_PORT): str,
            vol.Optional(CONF_BAUDRATE, default=9600): int,
            vol.Optional(CONF_MODBUS_ID, default=1): int,
            vol.Required(CONF_SENSOR_MODEL, default=self.templates[0] if self.templates else MODEL_CUSTOM): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=self.templates,
                    mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
        })

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
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
        """Handle the second step (Mapping Registers)."""
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
        
        if selected_model != MODEL_CUSTOM:
            if selected_model in self.loaded_templates:
                defaults = self.loaded_templates[selected_model]
            else:
                await self.hass.async_add_executor_job(self._load_templates)
                if selected_model in self.loaded_templates:
                    defaults = self.loaded_templates[selected_model]

        schema_dict = {}
        entity_name_default = selected_model if selected_model != MODEL_CUSTOM else "Irradiance Sensor"
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

