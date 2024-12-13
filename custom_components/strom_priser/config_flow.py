from homeassistant import config_entries
import voluptuous as vol
from homeassistant.core import callback
from .const import DOMAIN

class LinjaPriserConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Linja Priser."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate the input
            api_key = user_input.get("api_key")
            metering_point_id = user_input.get("metering_point_id")

            if not api_key or not metering_point_id:
                errors["base"] = "invalid_data"
            else:
                # Save valid configuration
                return self.async_create_entry(
                    title="Linja Priser",
                    data=user_input
                )

        # Show the form for user input
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("metering_point_id"): str,
            }),
            errors=errors,
        )