
This cotek project is a custom component for Home Assistant allowing sensors to be collected via Bluetooth BLE using an RS-232 interface to a Cotek inverter also Go-Power.  It was developed and tested on a Raspberry Pi 4B 4GB running the Home Assistant OS (6.6.62-haos-raspi).

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


Instructions:

Place all code into a new directory "cotek" within Home Assistant's structure:  
/root/homeassistant/custom_components/cotek
It's recommended to install Advanced SSH & Web Terminal and File editor Add-Ons in order to manipulate the code.

Edit __init__.py to suit your com port.  This was quick a quick proof of concept.  Maybe will clean up one day and use HA's built-in configuration mechanisms.

There are dependences that Python requires, and since using the Home Assistant OS, updates have to be made inside the Home Assistant container to persist after a reboot.  This worked for me:

    docker exec -it $(docker ps -f name=homeassistant -q) /bin/sh
    pip install bleak configparser requests
    exit

Edit Home Assistant's configuration file configuration.yaml to recognize the custom component, add:

    cotek:

Restart Home Assistant.

You can now add the sensors to your dashboard.

Enjoy!
