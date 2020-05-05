"""
Setup for different kinds of Goldair climate devices
"""
from . import DOMAIN
from .const import (CONF_DEVICE_ID, CONF_TYPE, CONF_TYPE_DEHUMIDIFIER,
                    CONF_TYPE_FAN, CONF_TYPE_HEATER, CONF_DISPLAY_LIGHT, CONF_TYPE_AUTO)
from .dehumidifier.light import GoldairDehumidifierLedDisplayLight
from .fan.light import GoldairFanLedDisplayLight
from .heater.light import GoldairHeaterLedDisplayLight


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the Goldair climate device according to its type."""
    data = hass.data[DOMAIN][discovery_info[CONF_DEVICE_ID]]
    device = data['device']

    if discovery_info[CONF_TYPE] == CONF_TYPE_AUTO:
        discovery_info[CONF_TYPE] = await device.async_inferred_type()

        if discovery_info[CONF_TYPE] is None:
            raise ValueError(f"Unable to detect type for device {device.name}")

    if discovery_info[CONF_TYPE] == CONF_TYPE_HEATER:
        data[CONF_DISPLAY_LIGHT] = GoldairHeaterLedDisplayLight(device)
    elif discovery_info[CONF_TYPE] == CONF_TYPE_DEHUMIDIFIER:
        data[CONF_DISPLAY_LIGHT] = GoldairDehumidifierLedDisplayLight(device)
    elif discovery_info[CONF_TYPE] == CONF_TYPE_FAN:
        data[CONF_DISPLAY_LIGHT] = GoldairFanLedDisplayLight(device)

    if CONF_DISPLAY_LIGHT in data:
        async_add_entities([data[CONF_DISPLAY_LIGHT]])


async def async_setup_entry(hass, config_entry, async_add_entities):
    config = {**config_entry.data, **config_entry.options}
    discovery_info = {
        CONF_DEVICE_ID: config[CONF_DEVICE_ID],
        CONF_TYPE: config[CONF_TYPE],
    }
    await async_setup_platform(hass, {}, async_add_entities, discovery_info)
