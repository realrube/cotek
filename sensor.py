"""
This file is part of https://github.com/realrube/cotek.

cotek is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cotek is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cotek. If not, see <https://www.gnu.org/licenses/>.
"""

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import STATE_UNAVAILABLE
from . import SENSOR_COMMANDS  # Import SENSOR_COMMANDS from init.py

class CustomSensor(SensorEntity):
    def __init__(self, name, serial_service):
        self._name = name
        self._serial_service = serial_service
        self.entity_id = f"sensor.{name.lower()}"
        self._unique_id = f"custom_sensor_{name.lower()}"

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._serial_service.sensors.get(self._name, STATE_UNAVAILABLE)

    @property
    def unique_id(self):
        return self._unique_id

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    serial_service = hass.data['serial_service']
    sensors = []

    for name in SENSOR_COMMANDS:
        entity_id = f"sensor.{name.lower()}"
        if entity_id not in hass.states.async_entity_ids():
            sensors.append(CustomSensor(name, serial_service))
        else:
            existing_state = hass.states.get(entity_id).state
            serial_service.sensors[name] = float(existing_state) if existing_state != STATE_UNAVAILABLE else 0.0

    async_add_entities(sensors)
