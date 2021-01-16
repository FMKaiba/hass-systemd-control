import logging

import voluptuous as vol

from sysdmanager import SystemdManager

from homeassistant.helpers.typing import HomeAssistantType
from homeassistant.components.switch import (
    ENTITY_ID_FORMAT,
    PLATFORM_SCHEMA,
    SwitchEntity
)

from homeassistant.const import (
    CONF_NAME,
    CONF_ICON,
    STATE_OFF,
    STATE_ON
)

import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_ICON, CONF_SERVICE, CONF_SERVICES, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)


UNIT_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVICE): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
    }
)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_SERVICES): vol.Schema({cv.slug: UNIT_SCHEMA}),
    }
)

async def async_setup_platform(
    hass: HomeAssistantType,
    config: ConfigType,
    async_add_entities: Callable,
    discovery_info: Optional[DiscoveryInfoType] = None,
) -> None:
    devices = config.get(CONF_SERVICES, {})
    switches = []

    for object_id, device_config in devices.items():
        name = device_config.get(CONF_NAME, object_id )
        switches.append(
            SystemDSwitch(
                hass,
                object_id,
                name,
                device_config.get(CONF_ICON, object_id ),
                device_config.get(CONF_SERVICE, object_id )
            )
        )
        _LOGGER.debug("Adding device: %s", name )

    if not switches:
        _LOGGER.error("No switches added")
        return False

    async_add_entities(switches)


class SystemDSwitch(SwitchEntity):
    """Representation of Switch Sensor."""

    def __init__(self, hass, object_id, name, icon, service):
        """Initialize the switch."""
        self._name = name
        self._hass = hass
        self.entity_id = ENTITY_ID_FORMAT.format(object_id)
        self._state = False
        self._icon = icon
        self._service = service
        self._available = True

    @property
    def is_on(self):
        """Return is_on status."""
        return self._state

    async def async_turn_on(self, **kwargs):
        """Turn On method."""
        if( SystemdManager().start_unit(self._service) ):
            self._state = STATE_ON
#        self.schedule_update_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn Off method."""
        if( SystemdManager().stop_unit(self._service) ):
            self._state = STATE_OFF
#        self.schedule_update_ha_state()

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

    @property
    def should_poll(self):
        """Do not poll."""
        return False

    async def async_update(self):
        """Return sensor state."""
        if SystemdManager().is_active(self._service):
            self._state = STATE_ON
        else:
            self._state = STATE_OFF
        return False
