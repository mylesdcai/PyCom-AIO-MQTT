from mqtt import MQTTClient
from network import WLAN
import machine
import time
import pycom
import config

from machine import WDT

from pysense import Pysense
from SI7006A20 import SI7006A20
from LTR329ALS01 import LTR329ALS01
from MPL3115A2 import MPL3115A2,ALTITUDE,PRESSURE

def sub_cb(topic, msg):
   print(msg)

py = Pysense()
mp = MPL3115A2(py, mode=ALTITUDE) # Returns height in meters. Mode may also be set to PRESSURE, returning a value in Pascals
si = SI7006A20(py)
lt = LTR329ALS01(py)

pycom.heartbeat(False)

# color combos for LED
blue = 0x000010
red = 0x100000
green = 0x001000

yellow = 0x101000
liteblue = 0x001010
magenta = 0x100010

white = 0x101010

# initialize WDT
wdt = WDT(timeout = 5500)  # enable it with a timeout of 5.5 seconds
asleep = .1

wlan = WLAN(mode=WLAN.STA)
wlan.connect(SSID, auth=(WLAN.WPA2, PW), timeout = 5000)

while not wlan.isconnected():
    machine.idle()
    pycom.rgbled(red)

print("Connected to Wifi\n")
wdt.feed() #made it past the WLAN timeout loop error
pycom.rgbled(white)
time.sleep(asleep)

client = MQTTClient("fipy", "io.adafruit.com",user = AIOuser, password = AIOpw, port=8883, ssl = True)

client.set_callback(sub_cb)
client.connect()
time.sleep(asleep)
wdt.feed() #made it past the WLAN timeout loop error

# Silicon Labs Si7006-A20
print("sending Si7006 temperature: " + str(si.temperature()*1.8+32))
client.publish(topic="mylescai/feeds/voltaic-fern-Si-temp", msg=str(si.temperature()*1.8+32))
pycom.rgbled(green)
time.sleep(asleep)
wdt.feed() #made it past the WLAN timeout loop error

# NXP MPL3115A2
print("sending MPL3115A2 temperature: " + str(mp.temperature()*1.8+32))
client.publish(topic="mylescai/feeds/voltaic-fern-MPL-temp", msg=str(mp.temperature()*1.8+32))
pycom.rgbled(green)
time.sleep(asleep)
wdt.feed() #made it past the WLAN timeout loop error

print("sending humidity: " + str(si.humidity()))
client.publish(topic="mylescai/feeds/voltaic-fern-humidity", msg=str(si.humidity()))
pycom.rgbled(blue)
time.sleep(asleep)
wdt.feed() #made it past the WLAN timeout loop error

b,r = lt.light()
print("sending channel blue lux: " + str(b) + " and red lux: " + str(r))
client.publish(topic="mylescai/feeds/voltaic-fern-blue-light", msg=str(b))
client.publish(topic="mylescai/feeds/voltaic-fern-red-light", msg=str(r))
pycom.rgbled(yellow)
time.sleep(asleep)
wdt.feed() #made it past the WLAN timeout loop error

print("sending battery voltage: " + str(py.read_battery_voltage()))
client.publish(topic="mylescai/feeds/voltaic-fern-battery", msg=str(py.read_battery_voltage()))
pycom.rgbled(magenta)
time.sleep(asleep)
wdt.feed()

# time.sleep(60)
pycom.rgbled(liteblue)
time.sleep(.3)
wdt.feed() #made it past the WLAN timeout loop error

# 4 minutes sleep
machine.deepsleep(1000*60*4) #time.sleep runs at 265mA with wifi enabled. sleep is just delay (in seconds)
    # deepsleep is actual sleep, current consumption around 45mA (deepsleep in milliseconds)
