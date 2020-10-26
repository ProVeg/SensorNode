version = "0.3"
ssid = "ProVeg Guest"
psk = "IamProVeg!"
quietstartmins = 24 * 60 # Minutes after boot before alarms start
thresyellow = 1000
thresred = 1500

# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
import uos, machine
#uos.dupterm(None, 1) # disable REPL on UART(0)
import gc
#import webrepl
#webrepl.start()
gc.collect()

from ST7735 import TFT
from terminalfont import terminalfont
from machine import SPI, Pin, PWM, I2C
import network, utime
import math
import CCS811
import bme280_float as bme280
from ntptime import settime

speaker = Pin(15, Pin.OUT)
speaker(0)
nwake = Pin(0, Pin.OUT)
nwake(0)

spi = SPI(1, baudrate=27000000, polarity=0, phase=0)
tft=TFT(spi,16)
tft.init_7735(tft.BLACKTAB)
tft._rgb = True
tft._size = (128, 160)
i2c = I2C(scl=Pin(5), sda=Pin(4))
ccs = CCS811.CCS811(i2c=i2c, addr=90)
bme = bme280.BME280(i2c=i2c, mode=bme280.BME280_OSAMPLE_1)
sta_if = network.WLAN(network.STA_IF)

def do_connect():
	if not sta_if.isconnected():
		print('connecting to network...')
		sta_if.active(True)
		sta_if.connect(ssid, psk)
		while not sta_if.isconnected():	
			print(".", end="")
			utime.sleep(1)
	print('network config:', sta_if.ifconfig())

def beep(freq=1000, dur=.5):
    beeper = PWM(Pin(15), freq=freq, duty=512)
    utime.sleep(dur)
    beeper.deinit()

def sirene():
    for i in (622,466,622,466,622,466,622):
        beep(i)

def draw():
    tft.rotation(2)
    if (co2 < 400):
        tft.fill(TFT.WHITE)
    elif (co2 < thresyellow):
        tft.fill(TFT.GREEN)
    elif (co2 < thresred):
        tft.fill(TFT.YELLOW)
    else:
        tft.fill(TFT.RED)
    tft.text((1, 2), "CO2e ppm:", TFT.BLACK, terminalfont, 2)
    if (co2 < 400):
        tft.text((1, 22), " ---", TFT.BLACK, terminalfont, 4)
    else:
        tft.text((1, 22), " " + str(int(co2+0.5)), TFT.BLACK, terminalfont, 4)
    if (uptime < (quietstartmins*60)):
        tft.text((1, 22), "!", TFT.BLACK, terminalfont, 4)
    #tft.text((1, 54), "Value is not", TFT.BLACK, terminalfont, 1)
    #tft.text((1, 64), "reliable yet!", TFT.BLACK, terminalfont, 1)
    tft.text((1, 54), "Temp: {0:2.1f}  C".format(bmeval[0]), TFT.BLACK, terminalfont, 1)
    tft.circle((82, 55), 2, TFT.BLACK)
    tft.text((1, 64), "Pressure: {0:4d} hPa".format(int(bmeval[1]/100+0.5)), TFT.BLACK, terminalfont, 1)
    if bmeval[2] > 0:
        tft.text((1, 74), "Humidity: {0:2.1f}%".format(bmeval[2]), TFT.BLACK, terminalfont, 1)
    else:
        tft.text((1, 74), "No humidity sensor".format(bmeval[2]), TFT.BLACK, terminalfont, 1)
    #tft.text((2, 94), "Next user: 13:45", TFT.BLACK, terminalfont, 1)
    tft.text((1, 151), "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d} Z".format(nowtime[0],nowtime[1],nowtime[2],nowtime[3],nowtime[4]), TFT.BLACK, terminalfont, 1)
    tft.text((1, 141), "IP "+sta_if.ifconfig()[0], TFT.BLACK, terminalfont, 1)
    tft.text((1, 121), "ProVeg Sensor "+version, TFT.BLACK, terminalfont, 1)
    tft.text((1, 131), "Uptime "+str(uptime)+"s", TFT.BLACK, terminalfont, 1)

beep()
tft.fill(TFT.WHITE)
tft.text((1, 2), "ProVeg Sensor "+version, TFT.BLACK, terminalfont, 1)
tft.text((1, 12), "simon.kowalewski@", TFT.BLACK, terminalfont, 1)
tft.text((1, 22), "        proveg.com", TFT.BLACK, terminalfont, 1)
tft.text((1, 42), "https://github.com", TFT.BLACK, terminalfont, 1)
tft.text((1, 52), "/ProVeg/SensorNode", TFT.BLACK, terminalfont, 1)
tft.text((1, 72), "Getting on WiFi...", TFT.BLACK, terminalfont, 1)
do_connect()
tft.text((1, 82), "IP "+sta_if.ifconfig()[0], TFT.BLACK, terminalfont, 1)
tft.text((1, 102), "Getting time...", TFT.BLACK, terminalfont, 1)
settime()
starttime = utime.localtime()
tft.text((1, 112), "{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d} Z".format(starttime[0],starttime[1],starttime[2],starttime[3],starttime[4]), TFT.BLACK, terminalfont, 1)
tft.text((1, 132), "Starting app...", TFT.BLACK, terminalfont, 1)


minute = starttime[4]
hour = starttime[3]
day = starttime[2]
while True:
    co2 = 0
    nowtime = utime.localtime()
    uptime = utime.mktime(nowtime) - utime.mktime(starttime)
    bmeval = bme.read_compensated_data()
    if bmeval[2] > 0:
        ccs.put_envdata(humidity=bmeval[2],temp=bmeval[0])
    for i in range(5):
        utime.sleep(1)
        if ccs.data_ready():
            co2 += ccs.eCO2
        else:
            co2 -= 100000
    co2 /= 5
    draw()

    if nowtime[4] != minute:
        # Every minute
        if (uptime > (quietstartmins*60)):
            if co2 > thresred:
                sirene()
            elif co2 > thresyellow:
                beep()
        minute = nowtime[4]

    if nowtime[3] != hour:
        # Every hour
        try:
            settime()
        finally:
            hour = nowtime[3]
            minute = nowtime[4]

    if nowtime[2] != day:
        # Every day
        # Write baseline to file
        day = nowtime[2]
