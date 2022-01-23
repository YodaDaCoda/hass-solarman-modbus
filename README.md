# hass-solarman-modbus

## Home Assistant custom component for solar inverters that communicate over the solarmanv5 protocol.

Tested using LSW-3 model data logger stick attached to a Sofar inverter. Support for other data loggers / inverters is planned.

Polls the inverter / data logger every minute and updates the sensors accordingly.

## Setup
Configure with the IP address and serial number of the inverter / data logger. The port is normally 8899 but some devices may differ. You can retrieve the serial number of the inverter from its web interface.

## Acknowlegements
Thanks to jmccrohan for the amazing `pysolarmanv5` library.
Thanks to @KodeCR upon whose own solarman data logger codebase this is based.