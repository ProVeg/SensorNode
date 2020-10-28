# ProVeg Sensor Node Software

## Installation

* Install [Micropython](https://micropython.org/download/esp8266/) on the NodeMCU. The software was tested with 1.13, but should run on any recent version
* Edit main.py to setup for your environment
* Copy the .py and .mpy files from this directory to the Micropython file system, for example with [ampy](https://github.com/scientifichackers/ampy)
* Reboot

## Links to included libraries

* [CCS811](https://github.com/Notthemarsian/CCS811)
* [BME280](https://github.com/robert-hh/BME280)
* [ST7735](https://github.com/cheungbx/st7735-esp8266-micropython)