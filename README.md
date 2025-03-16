# cotek

This **cotek** project is a custom component for Home Assistant allowing sensors to be collected via an RS-232 interface to certain Cotek SC Series (possibly other) inverters also Dometic Go-Power IC-Series inverter/chargers.  After some online sleuthing, it seems that Cotek may have produced produced the Go-Power hardware for Dometic?  The protocol was determined by sniffing the data between the Go-Power device and its display unit.  It was later found that the Cotek SC manual contained some (but not all) of these commands.  It was developed and tested on a Raspberry Pi 4B 4GB running the Home Assistant OS (6.6.62-haos-raspi).


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


## Connecting hardware:

Requires a standard RS-232 port, in my case I used a generic USB to Serial adapter having an FTDI chip.

The port for the standard remote is a 6-pin RJ-11 jack, but you may use a 4-pin jack (standard analog phone cord) *taking note the pin numbers vary*.  Communications always takes place at 4800 baud, N81.  The Go-Power port is labeled "REMOTE" whereas the Cotek is labeled "RS-232 REMOTE".

| RJ11-6 | RJ11-4 | DB-9 | Signal (Computer Side) |
| ------ | ------ | ---- | -----------------------|
| 2      | 1      | 5    | GND
| 3      | 2      | 3    | TXD
| 4      | 3      | 2    | RXD


Consult the web to confirm the standard RJ-11 pin arrangement.  
If you're looing at the contacts, tab away from you, cable down, pin 1 is on the left.

      1         6
     _____________
    | | | | | | | |
    | | | | | | | |
    |             |
    |  _________  |
    |             |
    |             |
    |             |
    | ___________ |
          | |
          | |

## Instructions:

Place all code into a new directory "cotek" within Home Assistant's structure:  

    /root/homeassistant/custom_components/cotek
    
It's recommended to install Advanced SSH & Web Terminal and File editor Add-Ons in order to manipulate the code.

Edit \_\_init__.py to suit your com port.  This was quick a quick proof of concept.  Maybe will clean up one day and use HA's built-in configuration mechanisms.

There are Python modules required required for this code that are not included by default, and since using the Home Assistant OS, updates have to be made inside the Home Assistant container to persist after a reboot.  This worked for me:

    docker exec -it $(docker ps -f name=homeassistant -q) /bin/sh
    pip install bleak configparser requests
    exit

Edit Home Assistant's configuration file configuration.yaml to recognize the custom component, add:

    cotek:

Restart Home Assistant.

You can now add the various sensors to your dashboard.  The entities will be shown as sensor.inverter_grid_voltage for example.

In order to control the inverter and charger using this code, add a binary_sensors to your dashboard that shows the state of the inverter power and inverter (binary_sensor.inverter_state and binary_sensor.charger_state).  Then, add Interactions to the sensors cotek: toggle_inverter and cotek: toggle_charger respectively.  You can now click on the binary sensor and it will toggle!  It's a bit of a workaround because implementing a switch is a bit more complex and I found it too frustrating.

## Commands Sniffed:

In anyone is interested, this was what I found.  I compared them to what I could find in the menus.  I later found a Cotek manual and some were confirmed, but not all were in the manual.  The ones I wasn't sure about "?", I did not implement.

| Command           | Function                        |
| ----------------- | ------------------------------- |
| RLYST?            | Relay state?
| PLLERR?           | PLL Error?
| CHST?             | Charger state?
| VINV?             | Inverter voltage
| IINV?             | Inverter current
| PINV?             | Output power
| VGRID?            | Grid voltage
| IGRID?            | Grid current
| PGRID?            | Grid power
| VBAT?             | Battery voltage
| IBAT?             | Battery current
| ERR?              | Error?
| TBAT?             | Battery temperature 
| TENIR?            | ?
| TMOS1?            | MOSFET1 temp
| TMOS2?            | MOSFET2 temp
| TTR?              | Transformer temp
| FRQ?              | AC Frequency
| POWER ?           | Command 0 = Inverter off, 1 = Inverter on, ? = Query
| CHAOFF ?          | Command 0 = Charger on, 1 =  Charger off, ? = Query
| EQST?             | Equilization?
| EQSET?            | Equilization?
| FUNC <##>         | Select a function code (observed 0-26 and 28)
| SETT?             | Show the value of the function code
| SETT <calue>	    | Set a new value for the function code
| TYPE?             | Battery type?
| *IDN?             | Version?
| EXEC 00,5A,C3	    | Saw this periodically, maybe charge level setting?
| *RST              | Factory reset

## Enjoy!
