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

import asyncio
import serial_asyncio
from datetime import datetime
from homeassistant.helpers import discovery
from homeassistant.const import STATE_UNAVAILABLE, STATE_ON, STATE_OFF

SERIAL_PORT = '/dev/serial/by-id/usb-FTDI_US232B_FTBTMP72-if00-port0'
BAUD_RATE = 4800
LOOP_INTERVAL = 10  # seconds
TIMEOUT = 1  # seconds
RECONNECT_INTERVAL = 10  # seconds

SENSOR_COMMANDS = {
    "Inverter_Frequency": "FRQ?",
    "Inverter_Power": "PINV?",
    "Inverter_Voltage": "VINV?",
    "Inverter_Current": "IINV?",
    "Inverter_Grid_Voltage": "VGRID?",
    "Inverter_Grid_Current": "IGRID?",
    "Inverter_Grid_Power": "PGRID?",
    "Inverter_Battery_Voltage": "VBAT?",
    "Inverter_Battery_Current": "IBAT?",
    "Inverter_Battery_Temp": "TBAT?",
    "Inverter_MOSFET1_Temp": "TMOS1?",
    "Inverter_MOSFET2_Temp": "TMOS1?",
    "Inverter_Transformer_Temp": "TTR?",
    "Inverter_Power_Status": "POWER ?",
    "Inverter_Charger_Status": "CHAOFF ?"
}

CONTROL_COMMANDS = {
    "inverter_on": "POWER 1",
    "inverter_off": "POWER 0",
    "charger_on": "CHAOFF 0",
    "charger_off": "CHAOFF 1"
}

class SerialService:
    def __init__(self, hass):
        self.hass = hass
        self.reader = None
        self.writer = None
        self.sensors = {name: 0.0 for name in SENSOR_COMMANDS}
        self.inverter_state = STATE_OFF
        self.charger_state = STATE_OFF
        self.inverter_command = None
        self.charger_command = None

    async def connect(self):
        for name, command in SENSOR_COMMANDS.items():
            self.hass.states.async_set(f"sensor.{name.lower()}", STATE_UNAVAILABLE)
        self.hass.states.async_set("binary_sensor.inverter_state", STATE_OFF)
        self.hass.states.async_set("binary_sensor.charger_state", STATE_OFF)
        while True:
            try:
                self.reader, self.writer = await serial_asyncio.open_serial_connection(
                    url=SERIAL_PORT, baudrate=BAUD_RATE
                )
                break
            except Exception as e:
                self.hass.states.async_set("sensor.serial_status", STATE_UNAVAILABLE)
                await asyncio.sleep(RECONNECT_INTERVAL)

    async def send_command(self, command):
        try:
            self.writer.write(f"{command}\r\n".encode())
            await self.writer.drain()
            response = await asyncio.wait_for(self.reader.readuntil(b'=>'), timeout=TIMEOUT)
            return response.decode().strip()
        except (asyncio.TimeoutError, Exception) as e:
            return None

    async def update_sensors(self):
        for name, command in SENSOR_COMMANDS.items():
            response = await self.send_command(command)
            if response is None or not response.endswith('=>'):
                self.hass.states.async_set(f"sensor.{name.lower()}", STATE_UNAVAILABLE)
            else:
                try:
                    self.sensors[name] = float(response[:-2])
                    self.hass.states.async_set(f"sensor.{name.lower()}", self.sensors[name])
                    if name == "Inverter_Power_Status":
                        new_state = STATE_ON if self.sensors[name] == 1.0 else STATE_OFF
                        if new_state != self.inverter_state:
                            self.inverter_state = new_state
                            self.inverter_command = CONTROL_COMMANDS["inverter_on"] if new_state == STATE_ON else CONTROL_COMMANDS["inverter_off"]
                        self.hass.states.async_set("binary_sensor.inverter_state", new_state)
                    elif name == "Inverter_Charger_Status":
                        new_state = STATE_ON if self.sensors[name] == 0.0 else STATE_OFF
                        if new_state != self.charger_state:
                            self.charger_state = new_state
                            self.charger_command = CONTROL_COMMANDS["charger_on"] if new_state == STATE_ON else CONTROL_COMMANDS["charger_off"]
                        self.hass.states.async_set("binary_sensor.charger_state", new_state)
                except ValueError:
                    self.hass.states.async_set(f"sensor.{name.lower()}", STATE_UNAVAILABLE)

    async def loop(self):
        while True:
            if self.reader is None or self.writer is None:
                await self.connect()
            await self.update_sensors()
            if self.inverter_command:
                await self.send_command(self.inverter_command)
                self.inverter_command = None
            if self.charger_command:
                await self.send_command(self.charger_command)
                self.charger_command = None
            await asyncio.sleep(LOOP_INTERVAL)

    async def toggle_inverter(self):
        new_command = CONTROL_COMMANDS["inverter_off"] if self.inverter_state == STATE_ON else CONTROL_COMMANDS["inverter_on"]
        self.inverter_command = new_command

    async def toggle_charger(self):
        new_command = CONTROL_COMMANDS["charger_off"] if self.charger_state == STATE_ON else CONTROL_COMMANDS["charger_on"]
        self.charger_command = new_command

async def async_setup(hass, config):
    serial_service = SerialService(hass)
    await serial_service.connect()

    hass.data['serial_service'] = serial_service

    async def toggle_inverter_service(call):
        await serial_service.toggle_inverter()

    async def toggle_charger_service(call):
        await serial_service.toggle_charger()

    hass.services.async_register('cotek', 'toggle_inverter', toggle_inverter_service)
    hass.services.async_register('cotek', 'toggle_charger', toggle_charger_service)

    hass.loop.create_task(serial_service.loop())

    await discovery.async_load_platform(hass, 'sensor', 'cotek', {}, config)

    return True
