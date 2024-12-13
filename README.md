# Strøm Priser Home Assistant Integrasjon

Denne integrasjonen for Home Assistant lar deg hente, cache og vise strømpriser fra et eksternt API. Prisene inkluderer både energipriser og fastpriser, med beregning av totalpris per time.

## Funksjonalitet

- **Henter priser fra API:** Integrasjonen kobler til `https://test-nettleie-api.linja.no` og henter strømpriser for spesifikke "metering points".
- **Caching:** Prisene caches lokalt én gang per dag, slik at unødvendige API-kall unngås.
- **Totalpris per time:** Beregner totalpris som inkluderer energipriser og fastpriser.
- **Visning i Home Assistant:** Viser totalpris og relevante detaljer som attributter i Home Assistant.

---

## Installasjon

### 1. Oppsett av filstruktur
Plasser integrasjonen i Home Assistant sitt `custom_components`-katalog:

```
/config/custom_components/strom_priser/
    __init__.py
    sensor.py
    const.py
    manifest.json
```

Koden for disse filene er inkludert i dette prosjektet.

### 2. Legg til i `configuration.yaml`
For å aktivere integrasjonen, legg til følgende i `configuration.yaml`:

```yaml
sensor:
  - platform: strom_priser
    name: "Nåværende strømpris"
```

### 3. Start Home Assistant
Etter at filene er plassert riktig og `configuration.yaml` er oppdatert, start Home Assistant på nytt:

```bash
hass --script check_config
hass
```

Eller hvis du bruker Docker:

```bash
docker restart home-assistant
```

---

## Konfigurasjon

### Miljøvariabler i `const.py`
Definer relevante API-innstillinger i `const.py`:

```python
DOMAIN = "strom_priser"
API_URL = "https://test-nettleie-api.linja.no/api/v1/GridTariff/meteringpointsgridtariffs"
API_KEY = "din-api-nøkkel"
METERING_POINT_ID = "707057500025054294"
```

Erstatt `API_KEY` og `METERING_POINT_ID` med dine verdier.

### Caching
Prisene caches i filen `/config/custom_components/strom_priser_cache.json`. Denne oppdateres én gang per dag.

Eksempel på cache-fil:
```json
{
    "cached_date": "2024-12-13",
    "cached_prices": {
        "gridTariffCollections": [ ... ]
    }
}
```

---

## Sensorens Attributter
Integrasjonen viser totalpris som sensorens hovedverdi, med følgende attributter:

| Attributt            | Beskrivelse                        |
|----------------------|------------------------------------|
| `energy_price`       | Energipris for timen (NOK).       |
| `fixed_price_per_hour` | Fastpris per time (NOK).         |
| `total_price`        | Totalpris for timen (NOK).        |
| `currency`           | Valuta (NOK).                    |
| `start_time`         | Starttidspunkt for timen.         |
| `end_time`           | Slutttidspunkt for timen.         |

---

## Automatiseringer
Du kan bruke sensoren i automatiseringer for å styre strømbruk basert på pris:

```yaml
automation:
  - alias: "Bruk strøm når billig"
    trigger:
      - platform: numeric_state
        entity_id: sensor.navaerende_strompris
        below: 50
    action:
      - service: switch.turn_on
        entity_id: switch.varmtvannsbereder
```

---

## Testing og Feilsøking

### Debugging
- Sjekk Home Assistant-loggene for feil:
  ```bash
  tail -f /config/home-assistant.log
  ```

- Typiske feil:
  - **Ugyldig API-nøkkel:** Sjekk at `API_KEY` er korrekt.
  - **Manglende cache-fil:** Cachen opprettes ved første kjøring.

### Testing
1. Gå til Developer Tools > States i Home Assistant.
2. Finn sensoren `sensor.navaerende_strompris`.
3. Verifiser at totalpris og attributter vises korrekt.

---

## Videreutvikling

- **Optimalisering av caching:** Lagre kun relevante deler av responsen hvis minnebruk må reduseres.
- **Støtte for flere metering points:** Utvid integrasjonen til å håndtere flere ID-er.
- **Historikk:** Implementer lagring og visning av historiske priser i Home Assistant.

---

## Lisens
Dette prosjektet er lisensiert under [MIT-lisensen](https://opensource.org/licenses/MIT).

---

Lykke til med integrasjonen! Kontakt oss dersom du har spørsmål eller trenger hjelp. 😊

