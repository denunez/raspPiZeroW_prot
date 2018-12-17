# Library import (mdl.py contains model functions)
#import matplotlib
# hola mi pollita :^)
#matplotlib.use('Agg')
import os
import time
import math
import RPi.GPIO as GP
import modelo as mdl
import sys
#sys.path.append('/home/pi/Adafruit_Python_DHT')
#sys.path.append('/home/pi/Adafruit_Python_DHT/source')
import Adafruit_DHT as dht

# Parameters initialization
elap = 60
tstart = time.perf_counter()
tdet = 0
Tmin = 0
Tmax = 40
WD = 0
R = 0
sens = dht.DHT22
count = 0
vecT = []
vecH = []
vecWet = []
vecWD = []
vect = []

# GPIO setup and initialization for hum. and temp. sensor DHT22/AM2302
pinLED = 24
pinDHT = 17
GP.setwarnings(False)
GP.cleanup()
GP.setmode(GP.BCM)
GP.setup(pinLED,GP.OUT)

# Leaf wetness sensor initialization
YL40,address = mdl.rain()

# Main code
while elap > time.perf_counter() - tstart:
    # Humidity, temperature and wetness detection
    t = round(time.perf_counter() - tstart,2)
    print('Time passed: '+str(t)+' s')
    hum,temp = dht.read_retry(sens, pinDHT)
    wet = mdl.rain_loop(YL40,address)
    tdet,WD = mdl.measureWD(tdet,t,wet)
    if hum is not None and temp is not None and WD is not None:
        print('Temp = {0:0.1f}*C  Hum = {1:0.1f}%  WD = {2:0.1f} s'.format(temp,hum,WD))
        print('Leaf Sensor Resistance = {0:0.2f}'.format(wet)+'\n')
    else:
        print('Failed to get reading of H,T or WD. Try or check again.')
    # Calculations based on Elisa Gonzales-Dominguez et al.'s (2015) Botrytis model 


    # Alert (later to be a function)
    if (temp >= 20 and temp <= 30) and (hum >= 90 or WD >= 30):
        GP.output(pinLED,True)
    else:
        GP.output(pinLED,False)
    # Save Values
    vect.append(t)
    vecT.append(temp)
    vecH.append(hum)
    vecWet.append(wet)
    vecWD.append(WD)
    count += 1
    time.sleep(1)

print('Fin del código.')
