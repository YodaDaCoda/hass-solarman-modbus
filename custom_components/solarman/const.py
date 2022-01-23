"""Constants for the SolarMAN logger integration."""
from typing import Final
from enum import Enum

DOMAIN = "solarman-modbus"

SENSOR_VDC1: Final = "Voltage DC1"
SENSOR_IDC1: Final = "Current DC1"
SENSOR_VDC2: Final = "Voltage DC2"
SENSOR_IDC2: Final = "Current DC2"
SENSOR_VAC: Final = "Voltage AC"
SENSOR_IAC: Final = "Current AC"
SENSOR_FREQ: Final = "Frequency"
SENSOR_TEMP: Final = "Temperature"
SENSOR_PWR: Final = "Power"
SENSOR_ENERGY_DAY: Final = "Energy Today"
SENSOR_ENERGY_TOT: Final = "Energy Total"
SENSOR_HRS: Final = "Hours Total"

from homeassistant.const import (
    ELECTRIC_POTENTIAL_VOLT,
    ELECTRIC_CURRENT_AMPERE,
    POWER_WATT,
    POWER_KILO_WATT,
    TEMP_CELSIUS,
    FREQUENCY_HERTZ,
    ENERGY_KILO_WATT_HOUR,
    TIME_HOURS
)

from homeassistant.components.sensor import (
    SensorDeviceClass,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
)


class Device(Enum):
    LSW3 = 'LSW-3'

class Sensor(Enum):
    VDC1 = "Voltage DC1"
    IDC1 = "Current DC1"
    PDC1 = "Power DC1"
    VDC2 = "Voltage DC2"
    IDC2 = "Current DC2"
    PDC2 = "Power DC2"
    VAC = "Voltage AC"
    IAC = "Current AC"
    FREQ = "Frequency"
    TEMP = "Temperature"
    PWR = "Power"
    ENERGY_DAY = "Energy Today"
    ENERGY_TOT = "Energy Total"
    HRS = "Hours Total"

class SensorDefinition:
    """A definition of a sensor

    :param name: The human-readable name of the sensor
    :param device_class: The HomeAssistant class of the device, e.g. DEVICE_CLASS_VOLTAGE
    :param state_class: The HomeAssistant class of the device's state, e.g. STATE_CLASS_MEASUREMENT for one-off measurements or STATE_CLASS_TOTAL_INCREASING for measurements that count up
    :param unit: The units of the measurement, e.g. ELECTRIC_POTENTIAL_VOLT (volts), ELECTRIC_CURRENT_AMPERE (amps)
    :param mb_offset: The modbus register offset for this sensor reading
    :param mb_size: The size of this sensor reading in bytes in the modbus response. Most sensor readings are 2-bytes, some are more.
    :param mb_mult: A multiplier to apply to the raw modbus value to convert it into the appropriate units.
    """
    def __init__(
        self,
        name: str,
        device_class: str,
        state_class: str,
        unit: str,
        mb_offset: int,
        mb_size: int = 2,
        mb_mult: int = 1
    ):
        self.name = name
        self.device_class = device_class
        self.state_class = state_class
        self.unit = unit
        self.mb_offset = mb_offset
        self.mb_size = mb_size
        self.mb_mult = mb_mult

# NB: device sensors MUST be in order of mb_offset
SENSOR_DEFINITIONS: Final = {
    Device.LSW3: [
        SensorDefinition(
            name=Sensor.VDC1.value,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=ELECTRIC_POTENTIAL_VOLT,
            mb_offset=6,
            mb_size=2,
            mb_mult=0.1,
        ),
        SensorDefinition(
            name=Sensor.IDC1.value,
            device_class=SensorDeviceClass.CURRENT,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=ELECTRIC_CURRENT_AMPERE,
            mb_offset=7,
            mb_size=2,
            mb_mult=0.01,
        ),
        SensorDefinition(
            name=Sensor.VDC2.value,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=ELECTRIC_POTENTIAL_VOLT,
            mb_offset=8,
            mb_size=2,
            mb_mult=0.1,
        ),
        SensorDefinition(
            name=Sensor.IDC2.value,
            device_class=SensorDeviceClass.CURRENT,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=ELECTRIC_CURRENT_AMPERE,
            mb_offset=9,
            mb_size=2,
            mb_mult=0.01,
        ),
        SensorDefinition(
            name=Sensor.PDC1.value,
            device_class=SensorDeviceClass.POWER,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=POWER_WATT,
            mb_offset=10,
            mb_size=2,
            mb_mult=10,
        ),
        SensorDefinition(
            name=Sensor.PDC2.value,
            device_class=SensorDeviceClass.POWER,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=POWER_WATT,
            mb_offset=11,
            mb_size=2,
            mb_mult=10,
        ),
        SensorDefinition(
            name=Sensor.PWR.value,
            device_class=SensorDeviceClass.POWER,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=POWER_KILO_WATT,
            mb_offset=12, # might be 14, need to check this
            mb_size=2,
            mb_mult=0.01,
        ),
        SensorDefinition(
            name=Sensor.FREQ.value,
            device_class=SensorDeviceClass.FREQUENCY,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=FREQUENCY_HERTZ,
            mb_offset=14,
            mb_size=2,
            mb_mult=0.01,
        ),
        SensorDefinition(
            name=Sensor.VAC.value,
            device_class=SensorDeviceClass.VOLTAGE,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=ELECTRIC_POTENTIAL_VOLT,
            mb_offset=15,
            mb_size=2,
            mb_mult=0.1,
        ),
        SensorDefinition(
            name=Sensor.IAC.value,
            device_class=SensorDeviceClass.CURRENT,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=ELECTRIC_CURRENT_AMPERE,
            mb_offset=16,
            mb_size=2,
            mb_mult=0.01,
        ),
        SensorDefinition(
            name=Sensor.ENERGY_TOT.value,
            device_class=SensorDeviceClass.ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
            unit=ENERGY_KILO_WATT_HOUR,
            mb_offset=22,
            mb_size=4,
            mb_mult=1,
        ),
        SensorDefinition(
            name=Sensor.HRS.value,
            device_class=None,
            state_class=STATE_CLASS_TOTAL_INCREASING,
            unit=TIME_HOURS,
            mb_offset=24,
            mb_size=4,
            mb_mult=1,
        ),
        SensorDefinition(
            name=Sensor.ENERGY_DAY.value,
            device_class=SensorDeviceClass.ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
            unit=ENERGY_KILO_WATT_HOUR,
            mb_offset=25,
            mb_size=2,
            mb_mult=0.01,
        ),
        SensorDefinition(
            name=Sensor.TEMP.value,
            device_class=SensorDeviceClass.TEMPERATURE,
            state_class=STATE_CLASS_MEASUREMENT,
            unit=TEMP_CELSIUS,
            mb_offset=27,
            mb_size=2,
            mb_mult=1,
        ),

    ]
}