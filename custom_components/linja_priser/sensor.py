from homeassistant.components.sensor import SensorEntity
from .const import DOMAIN, API_URL
import requests
import logging
import json
from calendar import monthrange
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

class LinjaPriserSensor(SensorEntity):
    """Representation of a Linja Priser Sensor."""

    def __init__(self, api_key, metering_point_id, price_type):
        """Initialize the sensor."""
        self._api_key = api_key
        self._metering_point_id = metering_point_id
        self._price_type = price_type
        self._state = None
        self._attributes = {}
        self._hourly_prices = []  # Liste for priser per time
        #self._unique_id = f"linja_priser_{metering_point_id}"  # Generer en unik ID basert på målernummer
        self._unique_id = f"linja_{price_type}_{metering_point_id}"

        self._cachefile = f"/tmp/linja_priser_cache_{metering_point_id}.json"

    @property
    def unique_id(self):
        """Return the unique ID of the sensor."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Linja {self._price_type} ({self._metering_point_id})"

    @property
    def state(self):
        """Return the current state."""
        return self._state

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    def update(self):
        """Fetch new state data for the sensor."""
        data = self._get_cached_or_fresh_data()
        if not data:
            return

        try:
            # Finn antall dager i den nåværende måneden
            today = datetime.now()
            year = today.year
            month = today.month

            # monthrange returnerer (første ukedag, antall dager i måneden)
            _, days_in_month = monthrange(year, month)

            #print(f"Antall dager i måneden: {days_in_month}")
            fixed_price_per_hour = 0

            # Finn fastprisen
            for entry in data["gridTariffCollections"][0]["meteringPointsAndPriceLevels"]:
                for metering_point in entry["meteringPoints"]:

                    if metering_point["meteringPointId"] == self._metering_point_id:
                        fixed_price_id = metering_point["levelValue"]

                        fixed_prices = data["gridTariffCollections"][0]["gridTariff"][0]["tariffPrice"]["priceInfo"]["fixedPrices"]
                        
                        for fixed_price in fixed_prices[0]['priceLevels']:
                            if fixed_price["id"] == fixed_price_id:
                                monthly_total = fixed_price["monthlyTotal"]
                                fixed_price_per_hour = round( monthly_total / (days_in_month * 24), 2 )
                                break

            # Hent priser for hele dagen
            self._hourly_prices = []  # Tøm listen før oppdatering
            for hour_data in data["gridTariffCollections"][0]["gridTariff"][0]["tariffPrice"]["hours"]:
                energy_price = round( hour_data["energyPrice"]["total"] / 100 , 2 )
                total_price = round( energy_price + fixed_price_per_hour, 2 )

                self._hourly_prices.append({
                    "start_time": hour_data["startTime"],
                    "end_time": hour_data["expiredAt"],
                    "total_price": total_price,
                    "energy_price": energy_price,
                    "fixed_price_per_hour": fixed_price_per_hour,
                })

            # Sett nåværende time som hovedstate
            current_hour = datetime.now().strftime("%Y-%m-%dT%H:00:00+00:00")
            for hour in self._hourly_prices:
                if hour["start_time"] == current_hour:
                    if self._price_type == "energy_price":
                        self._state = hour["energy_price"]
                    elif self._price_type == "fixed_price_per_hour":
                        self._state = hour["fixed_price_per_hour"]
                    #self._state = hour["total_price"]
                    self._attributes = {
                        "energy_price": hour["energy_price"],
                        "fixed_price_per_hour": hour["fixed_price_per_hour"],
                        #"total_price": hour["total_price"],
                        "start_time": hour["start_time"],
                        "end_time": hour["end_time"],
                    }
                    break

        except KeyError as e:
            _LOGGER.error("Error parsing API response: %s", e)

    def _get_cached_or_fresh_data(self):
        today = datetime.now().date()
        cache = self._load_cache()
        cached_date = f"cached_date_{self._metering_point_id}"
        cached_prices = f"cached_prices_{self._metering_point_id}"

        if cache and cache.get(cached_date) == str(today):
            _LOGGER.info("Using cached data.")
            return cache.get(cached_prices)

        _LOGGER.info("Fetching fresh data from API.")
        fresh_data = self._fetch_prices_from_api()
        if fresh_data:
            self._save_cache({cached_date: str(today), cached_prices: fresh_data})
            return fresh_data

    def _fetch_prices_from_api(self):
        headers = {"x-api-key": self._api_key}
        payload = {"range": "today", "meteringPointIds": [self._metering_point_id]}
        response = requests.post(API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            _LOGGER.error("API request failed with status code %s", response.status_code)
            return None

    def _load_cache(self):
        try:
            with open(self._cachefile, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _save_cache(self, data):
        try:
            with open(self._cachefile, "w") as f:
                json.dump(data, f)
        except Exception as e:
            _LOGGER.error("Failed to save cache: %s", e)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Linja Priser sensor from a config entry."""
    api_key = config_entry.data["api_key"]
    metering_point_id = config_entry.data["metering_point_id"]
    price_type = config_entry.data["price_type"]
    async_add_entities([
        LinjaPriserSensor(api_key, metering_point_id, price_type)
    ])