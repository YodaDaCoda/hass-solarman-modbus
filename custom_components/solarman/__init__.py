"""The SolarMAN logger integration."""
from __future__ import annotations
from asyncio.streams import StreamReader, StreamWriter

import logging

from homeassistant.config_entries import ConfigType, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_DEVICE_ID

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]


# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     """Set up the SolarMAN logger component."""
#     hass.data.setdefault(DOMAIN, {})
#     return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SolarMAN logger from a config entry."""
    _LOGGER.debug(f'__init__.py:async_setup_entry({entry.as_dict()})')
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug(f'__init__.py:async_unload_entry({entry.as_dict()})')
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN][entry.entry_id].sock.close()
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    _LOGGER.debug(f'__init__.py:update_listener({entry.as_dict()})')
    hass.data[DOMAIN][entry.entry_id].config(entry)
    entry.title = entry.options[CONF_HOST]

