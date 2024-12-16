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
            api_key = user_input.get("api_key")
            metering_point_id = user_input.get("metering_point_id")
            price_type = user_input.get("price_type")

            # Validate input
            valid_price_types = ["energy_price", "fixed_price_per_hour"]
            if not api_key or not metering_point_id:
                errors["base"] = "invalid_data"
            elif price_type not in valid_price_types:
                errors["price_type"] = "invalid_price_type"
            else:
                # Save valid configuration
                return self.async_create_entry(
                    title=f"Metering Point {price_type} {metering_point_id}",
                    data=user_input
                )

        # Show the form for user input
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("api_key"): str,
                vol.Required("metering_point_id"): str,
                vol.Required("price_type", default="energy_price"): vol.In(["energy_price", "fixed_price_per_hour"]),
            }),
            errors=errors,
        )
