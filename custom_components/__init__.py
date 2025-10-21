"""Football Data Multi custom component voor Home Assistant."""
import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .coordinator import FootballDataCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Setup van Football Data Multi via config entry."""
    api_token = entry.data.get("api_token")
    
    # Competitions komen uit options (als die er zijn) of uit data (oude installaties)
    competitions = entry.options.get("competitions", entry.data.get("competitions", ["DED"]))
    
    if not api_token:
        _LOGGER.error("Geen API token gevonden voor Football Data Multi")
        return False

    _LOGGER.info(f"Setting up Football Data Multi voor competities: {competitions}")

    # Maak coordinator aan
    coordinator = FootballDataCoordinator(
        hass, 
        api_token, 
        competitions, 
        update_interval=300  # 5 minuten
    )
    
    # Eerste refresh
    await coordinator.async_config_entry_first_refresh()
    
    # Debug: log wat er in de data zit
    _LOGGER.info(f"Coordinator data na eerste refresh: {list(coordinator.data.keys())}")
    for code, comp_data in coordinator.data.items():
        next_match = comp_data.get("next_match")
        if next_match:
            _LOGGER.info(
                f"Competitie {code} - Next match: {next_match.get('homeTeam', {}).get('name')} - {next_match.get('awayTeam', {}).get('name')}"
            )
        else:
            _LOGGER.warning(f"Competitie {code} - GEEN next_match gevonden in coordinator data!")

    # Sla coordinator op in hass.data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward naar sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    # Luister naar options updates
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    _LOGGER.info("Options gewijzigd, herladen van integratie...")
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok