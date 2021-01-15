"""Platform for Wattio integration testing."""
import logging

import voluptuous as vol

from sysdmanager import SystemdManager

try:
    from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity

from homeassistant.const import (
    CONF_NAME,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN
)

import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_ICON, CONF_SERVICE, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SERVICE): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
    }

)

async def async_setup_platform(hass: HomeAssistantType, config, async_add_entities, discovery_info=None):
    service = config[CONF_SERVICE]
    name = config[CONF_NAME]
    icon = config[CONF_ICON]
    
    _LOGGER.debug("Adding device: %s", name )

    async_add_entities([SystemDSwitch( name, icon, service )])


class SystemDSwitch(SwitchEntity):
    """Representation of Switch Sensor."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, name, icon, service):
        """Initialize the switch."""
        self._name = name
        self._state = False
        self._icon = icon
        self._service = service
        self._available = True

    @property
    def is_on(self):
        """Return is_on status."""
        return self._state

    async def async_turn_on(self):
        """Turn On method."""
        if( SystemdManager().start_unit(self._service) ):
            self._state = STATE_ON

    async def async_turn_off(self):
        """Turn Off method."""
        if( SystemdManager().stop_unit(self._service) ):
            self._state = STATE_OFF

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Return the image of the sensor."""
        return self._icon

    @property
    def available(self):
        """Return availability."""
        return self._available

    async def async_update(self):
        """Return sensor state."""
        if SystemdManager().is_active(self._service):
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
        return False
