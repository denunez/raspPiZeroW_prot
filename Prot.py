# Library import (mdl.py contains model functions)
#import matplotlib
#matplotlib.use('Agg')
import os
import time
import math
import RPi.GPIO as GP
import modelo as mdl
import modelo2 as mdl2
import sys
#sys.path.append('/home/pi/Adafruit_Python_DHT')
#sys.path.append('/home/pi/Adafruit_Python_DHT/source')
import Adafruit_DHT as dht
import DFA

# Parameters initialization
elap = 200
tdet,tdet2 = 0,0
thum = 0
hour,minute = 0,0
Tmin,Tmax = 0,40
WD = 0
R = 0
sens = dht.DHT22
count = 0
vecC,vect,vecT,vecH,vecWet,vecWD,vecIndex,vecRiskBr = ([] for i in range(8))
CISOi,vecRIS1,vecRIS2,vecRIS3 = ([] for i in range(4))
vecSEV1,vecSEV2,vecSEV3 = ([] for i in range(3))
alert1,alert2 = ([] for i in range(2))

# GPIO setup and initialization for hum. and temp. sensor DHT22/AM2302
pinLED = 24
pinDHT = 17
GP.setwarnings(False)
GP.cleanup()
GP.setmode(GP.BCM)
GP.setup(pinLED,GP.OUT)

# Leaf wetness sensor initialization
YL40,address = mdl.rain()

# Input Variables
#GS1 = int(input('Current Growth Stage RIS1: '))
#GS2 = int(input('Current Growth Stage for RIS2,RIS3: '))
GS1 = 57
GS2 = 89
tstart = time.perf_counter()

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
        print('Leaf Sensor Resistance = {0:0.2f}'.format(wet))
    else:
        print('Failed to get reading of H,T or WD. Try or check again.')

    # Calculations based on Elisa Gonzalez-Dominguez et al.'s (2015) Botrytis model
    Teq = (temp-Tmin)/(Tmax-Tmin)
    hrAnt = hour
    minAnt = minute
    hour = mdl.hourPass(t,hour)
    minute = mdl.minutePass(t,minute)
    Mf = mdl.Mf(R,WD,hum,thum,mdl.hourComp(hrAnt,hour),mdl.hourComp(minAnt,minute))
    thum = Mf*60
    MYGRn = mdl.MYGR(Teq)*Mf
    SPORn = mdl.SPOR(Teq,hum)
    CISOdia = MYGRn*SPORn
    CISOi.append(CISOdia)
    if len(CISOi) >= 7:
        CISOi.pop(0)
    CISOsem = mdl.CISO(CISOi)
    SUS1 = mdl.SUS1(GS1)                     # 1st infection window risk calcuations
    INF1 = mdl.INF1(Teq,WD,GS1)
    RIS1 = mdl.RIS1(CISOsem,Teq,WD,GS1)
    vecRIS1.append(RIS1)
    SUS2 = mdl.SUS2(GS2)                     # 2nd infection window risk calculations
    INF2 = mdl.INF2(Teq,WD,GS2)
    RIS2 = mdl.RIS2(CISOsem,Teq,WD,GS2)
    vecRIS2.append(RIS2)
    SUS3 = mdl.SUS3(GS2)
    INF3 = mdl.INF3(Teq,hum,GS2)
    RIS3 = mdl.RIS3(Teq,hum,GS2)*Mf
    vecRIS3.append(RIS3)

    # Calculations based on Broome et al.s' (1995) Botrytis model.
    tdet2,wd = mdl2.calcWD(tdet2,t,wet,hum)
    index = mdl2.calcIndex(temp,wd)



    # Alert (later to be a function)
    if (temp >= 20 and temp <= 30) and (hum >= 90 or WD >= 30):
        GP.output(pinLED,True)
    else:
        GP.output(pinLED,False)

    ## According to 1st model



    ## According to 2nd model
    degree2 = mdl2.degreeRisk(index)
    mdl2.raiseAlert(degree2)


    # Save Parameter Values
    vecC.append(count)
    vect.append(t)
    vecT.append(temp)
    vecH.append(hum)
    vecWet.append(wet)
    vecWD.append(WD)
    vecIndex.append(index)
    vecRiskBr.append(degree2)

    # SEV calculations
    SEV1 = mdl.SEV(vecRIS1)
    SEV2 = mdl.SEV(vecRIS2)
    SEV3 = mdl.SEV(vecRIS3)
    vecSEV1.append(SEV1)
    vecSEV2.append(SEV2)
    vecSEV3.append(SEV3)

    # Loop counting and code sleep
    count += 1
    time.sleep(1)
    print(count,Mf,t,temp,hum,wet,WD,index,degree2,RIS1,RIS2,RIS3)

# Datalogging
mdl.writeCsv(vecC,vect,vecT,vecH,vecWD,vecWet,vecIndex,vecRiskBr,vecRIS1,vecRIS2,vecRIS3)


GP.cleanup()
print('Fin del código.')

