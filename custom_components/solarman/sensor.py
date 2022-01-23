"""Platform for SolarMAN logger sensor integration."""
from __future__ import annotations

import logging

from datetime import timedelta

import asyncio
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.util.dt import utc_from_timestamp
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.components.sensor import (
    SensorEntity,
)
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_DEVICE,
    CONF_DEVICE_ID,
)

from .const import (
    DOMAIN,
    Device,
    SENSOR_DEFINITIONS,
)

from .pysolarmanv5.pysolarmanv5 import PySolarmanV5

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Config entry example."""

    _LOGGER.debug(f'sensor.py:async_setup_entry:({entry.options})')

    async def async_update_data():
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        _LOGGER.debug(f'sensor.py:async_setup_entry.async_update_data: refresh')
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with async_timeout.timeout(60):
                return await inverter.async_update_data()
        except OSError as err:
            raise UpdateFailed(f"Error communicating with inverter: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        # Name of the data. For logging purposes.
        name="sensor",
        update_method=async_update_data,
        # Polling interval. Will only be polled if there are subscribers.
        update_interval=timedelta(seconds=30),
    )
    _LOGGER.debug(f'sensor.py:async_setup_entry: got update coordinator {coordinator}')

    inverter = Inverter(hass, entry=entry, device=Device[entry.options[CONF_DEVICE]])
    _LOGGER.debug(f'sensor.py:async_setup_entry: got inverter {inverter}')

    sensors = [SolarMANSensor(inverter=inverter, definition=definition, coordinator=coordinator) for definition in SENSOR_DEFINITIONS[inverter.device]]
    inverter.set_sensors(sensors)
    _LOGGER.debug(f'sensor.py:async_setup_entry: sensors created')

    #
    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    _LOGGER.debug(f'sensor.py:async_setup_entry: first refresh')
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(sensors)

class Inverter:
    """The solar inverter."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, device: str) -> None:
        """Init solar inverter."""
        _LOGGER.debug(f'sensor.py:Inverter.__init__({entry.as_dict()})')
        self._hass = hass
        self.host = ""
        self.port = 0
        self.server = None
        self.data = {}
        self.raw_data = []
        self.device = device
        self.sensor_list = []
        self.sensors_dict = {}
        self.config(entry)

    def config(self, entry: ConfigEntry) -> None:
        _LOGGER.debug(f'sensor.py:Inverter.config({entry.as_dict()})')
        self.host = entry.options[CONF_HOST]
        self.port = entry.options[CONF_PORT]
        self.serial = entry.options[CONF_DEVICE_ID]
        self._modbus = None

    def set_sensors(self, sensors: list[SolarMANSensor]):
        self.sensor_list = sensors
        self.sensors_dict = {sensor.name: sensor for sensor in sensors}

    async def async_update_sensors(self):
        _LOGGER.debug('sensor.py:Inverter.async_update_sensors')
        _LOGGER.debug(f'sensor.py:Inverter.async_update_sensors: sensors: {self.sensor_list}')
        await asyncio.gather(*[sensor.async_update_value(dict(enumerate(self.raw_data)).get(sensor.mb_offset)) for sensor in self.sensor_list])

    def create_connection(self):
        _LOGGER.debug(f'sensor.py:Inverter.create_connection: instantiating modbus interface')
        # TODO: somehow we need to catch error from endpoint unavailable and mark entity as gone
        # e.g. when the sun goes down and the logger is unpowered
        if self._modbus and self._modbus.sock:
            try:
                self._modbus.sock.close()
            except:
                pass
        self._modbus = PySolarmanV5(
            address=self.host, serial=self.serial, port=self.port, mb_slave_id=1, verbose=1
        )
        _LOGGER.debug(f'sensor.py:Inverter.create_connection: modbus interface instantiated')

    def _get_modbus_size(self):
        # the size is the maximum offset plus the size of that register
        # sensors are ordered by their offset, so just grab the last one
        return self.sensor_list[-1].mb_offset + self.sensor_list[-1].mb_size

    def retrieve_raw_data(self):
        _LOGGER.debug('sensor.py:Inverter.retrieve_raw_data')
        self.create_connection()
        data = {}
        try:
            data = self._modbus.read_holding_registers(register_addr=0, quantity=self._get_modbus_size())
        except IOError as e:
            _LOGGER.debug('Exception reading registers')
            _LOGGER.debug(e)
        except OSError as e:
            _LOGGER.debug('Exception reading registers')
            _LOGGER.debug(e)
        _LOGGER.debug(f'sensor.py:Inverter.retrieve_raw_data: raw_data: {data}')
        self.raw_data = data

    async def async_update_data(self):
        _LOGGER.debug('sensor.py:Inverter.async_update_data')
        self.retrieve_raw_data()
        await self.async_update_sensors()
        return self.sensor_list


class SolarMANSensor(CoordinatorEntity, SensorEntity):
    """Representation of a SolarMAN logger device."""

    def __init__(self, inverter, definition, coordinator):
        """Initialize the sensor."""

        _LOGGER.debug(f'sensor.py:SolarMANSensor.__init__({definition})')
        _LOGGER.debug(f'sensor.py:SolarMANSensor.__init__: name: {definition.name}, device_class: {definition.device_class}, state_class: {definition.state_class}, unit: {definition.unit}, mb_offset: {definition.mb_offset}, mb_size: {definition.mb_size}, mb_mult: {definition.mb_mult}')

        self._inverter = inverter
        self._definition = definition
        self.coordinator = coordinator

        self.online = False
        self.raw_value = None

    async def async_update_value(self, value):
        _LOGGER.debug(f'sensor.py:SolarMANSensor.async_update_value({value})')
        self.raw_value = value
        if value:
            self.online = True
        else:
            self.online = False
        _LOGGER.debug(f'sensor.py:SolarMANSensor.async_update_value: name: {self.name}, raw_value: {value}, value: {self.value}{self.native_unit_of_measurement}')
        await self.coordinator.async_request_refresh()

    @property
    def mb_size(self):
        return self._definition.mb_size

    @property
    def mb_offset(self):
        return self._definition.mb_offset

    @property
    def value(self):
        if self.raw_value:
            return self.raw_value * self._definition.mb_mult
        return None

    @property
    def unique_id(self):
        """Return unique id."""
        return f"{DOMAIN}_{self._inverter.serial}_{self._definition.name}"

    @property
    def name(self):
        """Name of this inverter attribute."""
        return f'{self._inverter.serial} {self._definition.name}'

    @property
    def device_class(self):
        """State of this inverter attribute."""
        return self._definition.device_class

    @property
    def state_class(self):
        """State of this inverter attribute."""
        return self._definition.state_class

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._definition.unit

    @property
    def native_value(self):
        """State of this inverter attribute."""
        return self.value

    @property
    def should_poll(self) -> bool:
        """No polling needed."""
        return False

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.online

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this device."""
        return {
            "identifiers": {(DOMAIN, self._inverter.serial)},
            "name": f"SolarMAN Logger {self._inverter.serial}",
            "manufacturer": "IGEN Tech",
            "model": self._inverter.device.value,
        }
