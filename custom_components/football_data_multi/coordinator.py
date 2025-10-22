"""Football Data Multi Coordinator voor Home Assistant."""
import logging
from datetime import timedelta
import asyncio
import aiohttp

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import BASE_URL

_LOGGER = logging.getLogger(__name__)

class FootballDataCoordinator(DataUpdateCoordinator):
    """Haalt data op van meerdere Football-Data.org competities."""

    def __init__(self, hass, api_token, competitions, update_interval=300):
        super().__init__(
            hass,
            _LOGGER,
            name="Football Data Multi Coordinator",
            update_interval=timedelta(seconds=update_interval),
        )
        self._headers = {"X-Auth-Token": api_token}
        self._competitions = competitions

    async def _get_json(self, session, url):
        """Haalt JSON op met foutafhandeling."""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.get(url, headers=self._headers, timeout=timeout) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise UpdateFailed(f"API-fout {resp.status}: {text}")
                return await resp.json()
        except asyncio.TimeoutError:
            raise UpdateFailed(f"Timeout bij ophalen van {url}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Client error bij ophalen van {url}: {err}")

    async def _safe_get(self, session, url):
        """Helper die fouten opvangt maar de coordinator laat doorlopen."""
        try:
            return await self._get_json(session, url)
        except UpdateFailed as err:
            _LOGGER.warning("Kon data niet ophalen van %s: %s", url, err)
            return {}

    async def _fetch_competition_data(self, session, code):
        """Haalt data op voor één competitie."""
        _LOGGER.info("=== Ophalen data voor competitie %s ===", code)

        standings = await self._safe_get(session, f"{BASE_URL}/competitions/{code}/standings")
        live = await self._safe_get(session, f"{BASE_URL}/competitions/{code}/matches?status=LIVE")
        
        # Gebruik /competitions/{code}/matches zoals in het werkende testscript
        scheduled = await self._safe_get(session, f"{BASE_URL}/competitions/{code}/matches?status=SCHEDULED")

        matches_count = len(scheduled.get('matches', []))
        _LOGGER.info("Scheduled voor %s: %s wedstrijden gevonden", code, matches_count)
        
        if matches_count > 0:
            first_match = scheduled.get("matches", [])[0]
            _LOGGER.info(
                "Eerste match (ongesorteerd): %s - %s op %s",
                first_match.get("homeTeam", {}).get("name"),
                first_match.get("awayTeam", {}).get("name"),
                first_match.get("utcDate")
            )

        total_stand = next(
            (s for s in standings.get("standings", []) if s.get("type") == "TOTAL"),
            {},
        )

        matches = scheduled.get("matches", [])
        matches.sort(key=lambda x: x.get("utcDate", ""))
        next_match = matches[0] if matches else None

        if next_match:
            _LOGGER.warning(
                "=== Next match voor %s: %s - %s op %s ===",
                code,
                next_match.get('homeTeam', {}).get('name'),
                next_match.get('awayTeam', {}).get('name'),
                next_match.get('utcDate')
            )
        else:
            _LOGGER.error("=== GEEN next_match voor %s! ===", code)

        result = {
            "standings": total_stand.get("table", []),
            "live_matches": live.get("matches", []),
            "next_match": next_match,
        }
        
        _LOGGER.warning("Result voor %s: keys=%s, next_match is None=%s", code, list(result.keys()), result["next_match"] is None)
        
        return result

    async def _async_update_data(self):
        """Haalt alle competities op."""
        data = {}
        async with aiohttp.ClientSession() as session:
            for code in self._competitions:
                try:
                    data[code] = await self._fetch_competition_data(session, code)
                except Exception as err:
                    _LOGGER.error("Fout bij competitie %s: %s", code, err, exc_info=True)
                    data[code] = {}

        _LOGGER.info("Football Data update voltooid voor competities: %s", ", ".join(self._competitions))
        return data