"""Football Data Multi sensoren."""
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, COMPETITIONS

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    """Setup sensors voor elke geselecteerde competitie."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    # Haal competitions uit options of data
    competitions = entry.options.get("competitions", entry.data.get("competitions", ["DED"]))
    
    entities = []

    for code in competitions:
        name = COMPETITIONS.get(code, code)
        entities.append(FootballStandingsSensor(coordinator, code, name))
        entities.append(FootballNextMatchSensor(coordinator, code, name))
        entities.append(FootballLiveMatchSensor(coordinator, code, name))

    _LOGGER.info("Setting up %d sensors voor competities: %s", len(entities), competitions)
    async_add_entities(entities)


class BaseFootballSensor(CoordinatorEntity, SensorEntity):
    """Basis klasse voor alle sensoren."""

    def __init__(self, coordinator, code, name, sensor_type, icon):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.code = code
        self._competition_name = name
        self._attr_name = f"{name} {sensor_type}"
        self._attr_icon = icon
        self._attr_unique_id = f"{code.lower()}_{sensor_type.lower().replace(' ', '_')}"

    @property
    def device_info(self):
        """Return device info to group sensors per competition."""
        return {
            "identifiers": {(DOMAIN, self.code)},
            "name": self._competition_name,
            "manufacturer": "Football-Data.org",
            "model": f"{self.code} Competition",
            "entry_type": "service",
        }

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success and self.code in self.coordinator.data


class FootballStandingsSensor(BaseFootballSensor):
    """Standings per competitie."""

    def __init__(self, coordinator, code, name):
        super().__init__(coordinator, code, name, "Stand", "mdi:trophy")

    @property
    def native_value(self):
        table = self.coordinator.data.get(self.code, {}).get("standings", [])
        if not table:
            return "Onbekend"
        leader = table[0]
        return f"{leader['team']['name']} ({leader['points']}p)"

    @property
    def extra_state_attributes(self):
        table = self.coordinator.data.get(self.code, {}).get("standings", [])
        return {
            "standings": [
                {
                    "position": t["position"],
                    "team": {
                        "name": t["team"]["name"],
                        "crest": t["team"]["crest"],
                    },
                    "playedGames": t["playedGames"],
                    "won": t["won"],
                    "draw": t["draw"],
                    "lost": t["lost"],
                    "points": t["points"],
                    "goalsFor": t["goalsFor"],
                    "goalsAgainst": t["goalsAgainst"],
                    "goalDifference": t["goalDifference"],
                }
                for t in table
            ]
        }


class FootballNextMatchSensor(BaseFootballSensor):
    """Volgende geplande wedstrijd per competitie."""

    def __init__(self, coordinator, code, name):
        super().__init__(coordinator, code, name, "Volgende Wedstrijd", "mdi:calendar-clock")

    @property
    def native_value(self):
        comp_data = self.coordinator.data.get(self.code, {})
        next_match = comp_data.get("next_match")
        
        # Uitgebreide debug logging
        _LOGGER.warning(
            "NextMatchSensor %s - coordinator.data: %s",
            self.code,
            self.coordinator.data
        )
        _LOGGER.warning(
            "NextMatchSensor %s - comp_data keys: %s, next_match type: %s, next_match: %s",
            self.code,
            list(comp_data.keys()),
            type(next_match),
            next_match
        )
        
        if not next_match:
            _LOGGER.error("NextMatchSensor %s - next_match is NONE or EMPTY!", self.code)
            return "Geen gepland"
        
        home = next_match.get("homeTeam", {}).get("name", "?")
        away = next_match.get("awayTeam", {}).get("name", "?")
        _LOGGER.info("NextMatchSensor %s - Returning: %s - %s", self.code, home, away)
        return f"{home} - {away}"

    @property
    def extra_state_attributes(self):
        next_match = self.coordinator.data.get(self.code, {}).get("next_match")
        if not next_match:
            return {}
        
        return {
            "datum": next_match.get("utcDate"),
            "status": next_match.get("status"),
            "matchday": next_match.get("matchday"),
            "thuisteam": next_match.get("homeTeam", {}).get("name"),
            "thuisteam_crest": next_match.get("homeTeam", {}).get("crest"),
            "uitteam": next_match.get("awayTeam", {}).get("name"),
            "uitteam_crest": next_match.get("awayTeam", {}).get("crest"),
        }


class FootballLiveMatchSensor(BaseFootballSensor):
    """Live wedstrijden per competitie."""

    def __init__(self, coordinator, code, name):
        super().__init__(coordinator, code, name, "Live Wedstrijden", "mdi:soccer")

    @property
    def native_value(self):
        matches = self.coordinator.data.get(self.code, {}).get("live_matches", [])
        return len(matches)

    @property
    def extra_state_attributes(self):
        matches = self.coordinator.data.get(self.code, {}).get("live_matches", [])
        if not matches:
            return {"matches": []}
        
        return {
            "matches": [
                {
                    "home_team": m.get("homeTeam", {}).get("name"),
                    "home_crest": m.get("homeTeam", {}).get("crest"),
                    "away_team": m.get("awayTeam", {}).get("name"),
                    "away_crest": m.get("awayTeam", {}).get("crest"),
                    "score_home": m.get("score", {}).get("fullTime", {}).get("home"),
                    "score_away": m.get("score", {}).get("fullTime", {}).get("away"),
                    "status": m.get("status"),
                    "minute": m.get("minute"),
                    "matchday": m.get("matchday"),
                }
                for m in matches
            ]
        }