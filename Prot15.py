# Library import (mdl15.py contains model functions to be executed every 15 minutes)
#import matplotlib
#matplotlib.use('Agg')
# polla ich liebe dich ;^)
import os
import time
import datetime
import math
import json
import RPi.GPIO as GP
import modelo15 as mdl15
import modelo2 as mdl2
import csv
import sys
#sys.path.append('/home/pi/Adafruit_Python_DHT')
#sys.path.append('/home/pi/Adafruit_Python_DHT/source')
import Adafruit_DHT as dht
import DFA
import requests

# Parameters initialization
min_exec = 15
elap = 60
Tmin,Tmax = 0,40
R = 0
sens = dht.DHT22
CISOi = []
hract = str(datetime.datetime.now())

# GPIO setup and initialization for hum. and temp. sensor DHT22/AM2302
pinLED = 24
pinDHT = 17
GP.setwarnings(False)
GP.cleanup()
GP.setmode(GP.BCM)
GP.setup(pinLED,GP.OUT)

# Leaf wetness sensor initialization
YL40,address = mdl15.rain()

# Input Variables
#GS1 = int(input('Current Growth Stage RIS1: '))
#GS2 = int(input('Current Growth Stage for RIS2,RIS3: '))
GS1 = 57
GS2 = 89
for i in range(3):
    tstart = int(round(time.time(),2))

######## Main code to be executed every 15 minutes via cronjob ########

# Open file with previous measurements data. If it doesn't exists creates one for appending

a = []
try:
    prev_data = open('datalog2.csv','r')
    r = csv.reader(prev_data,delimiter=',')
except IOError:
    new_data = open('datalog2.csv','w')
    f = csv.writer(new_data)
    h = ['UTS','Temp.','Hum.','WD','wd','LWSR','Index Br.','Risk Br.','CISOi','SPORn','RIS1','RIS2','RIS3','SEV1','SEV2','SEV3','tdet','tdet2','thum','tstart','tstop']
    f.writerow(h)
    x0 = [hract,25,50,0,0,11,-2.6,'No',0,0,0,0,0,0,0,0,0,0,0,tstart,0]
    f.writerow(x0)
    new_data.close()
    prev_data = open('datalog2.csv','r')
    r = csv.reader(prev_data,delimiter=',')
for row in r:
    a.append(row)
prev_data.close()
ap_data = open('datalog2.csv','a')
w = csv.writer(ap_data)

# Open file with rain measurements
ra = []
try:
    rain_data = open('rainlog.csv','r')
    rrd = csv.reader(rain_data,delimiter=',')
    for row in rrd:
        ra.append(row)
    rain_data.close()
    Rlast = float(ra[-1][1])
    R = Rlast-float(ra[-2][1])
except IOError:
    Rlast = 0
    R = 0
    ra = 0

# Humidity, temperature and wetness detection measurements (5 times for accuracy)
print(a)
print(ra)
print(Rlast)
print(R)

t = math.ceil(tstart-float(a[1][19]))
lol = time.localtime(t)
tdet = float(a[-1][16])
WD = float(a[-1][3])
wd = float(a[-1][4])
tstop = float(a[-1][20])
for i in range(5):
    hum,temp = dht.read_retry(sens,pinDHT)
    wet = mdl15.rain_loop(YL40,address)
    tdet,WD,tstop = mdl15.measureWD(tdet,t,wet,WD,tstop)
    if hum is not None and temp is not None and WD is not None:
        print('Temp = {0:0.1f}*C  Hum = {1:0.1f}%  WD = {2:0.2f} min'.format(temp,hum,WD))
        print('Leaf Sensor Resistance = {0:0.2f}'.format(wet))
    else:
        print('Failed to get reading of H,T or WD. Try or check again.')
    time.sleep(1)

print(hract)

# Calculations based on Elisa Gonzalez-Dominguez et al.'s (2015) Botrytis model
Teq = (temp-Tmin)/(Tmax-Tmin)
prevTime = a[-1][0][8:19]
currTime = hract[8:19]
thum = float(a[-1][18])
hour = float(currTime[3:5])
day = float(currTime[0:2])
print(currTime)
print(day)
print(hour)
hrAnt = float(prevTime[3:5])
dayAnt = float(prevTime[0:2])
prevHrRain = float(ra[-2][0][11:13])
currHrRain = float(ra[-1][0][11:13])
print(prevHrRain)
print(currHrRain)
print(mdl15.RP(prevHrRain,currHrRain))
Mf = mdl15.Mf(R,mdl15.RP(prevHrRain,currHrRain),WD,hum,thum,mdl15.hourComp(hrAnt,hour),mdl15.dayComp(dayAnt,day))
thum = Mf*24
MYGRn = mdl15.MYGR(Teq)*Mf
SPORn = mdl15.SPOR(Teq,hum)
CISOdia = MYGRn*SPORn
for i in range(len(a[1:])):
    CISOi.append(float(a[-(i+1)][8]))      # For now CISOi is defined as the last 7 measurements of CISO instead of average per day
while len(CISOi) >= 7:
    CISOi.pop(0)
CISOi.append(CISOdia)
CISOsem = mdl15.CISO(CISOi)
SUS1 = mdl15.SUS1(GS1)                     # 1st infection window risk calculations
INF1 = mdl15.INF1(Teq,WD,GS1)
RIS1 = CISOsem*INF1
SUS2 = mdl15.SUS2(GS2)                     # 2nd infection window risk calculations
INF2 = mdl15.INF2(Teq,WD,GS2)
RIS2 = CISOsem*INF2
SUS3 = mdl15.SUS3(GS2)                     # 3rd infection window risk calculations
INF3 = mdl15.INF3(Teq,hum,GS2)
RIS3 = MYGRn*INF3

# Calculating Function (same as above but with less code lines)
# Mf,CISOdia,RIS1,RIS2,RIS3,SEV1,SEV2,SEV3 = mdl15.mainCalc(a,Teq,hum,WD,GS1,GS2,thum)

# Calculations based on Broome et al.s' (1995) Botrytis model.
tdet2 = float(a[-1][17])
tdet2,wd = mdl2.calcWD(tdet2,t,wet,hum,wd)
index = mdl2.calcIndex(temp,wd)

# Alert (later to be a function)




## According to 1st model, probably with the use of a gradient function when RIS and SEV are constant and rises rapidly, respectively.



## According to 2nd model, index table of severity
degree2 = mdl2.degreeRisk(index)
mdl2.raiseAlert(degree2)


# SEV calculations
SEV1 = float(a[-1][13])+RIS1
SEV2 = float(a[-1][14])+RIS2
SEV3 = float(a[-1][15])+RIS3

# Sending data to cloud in dweet.io for data storage
try:
    dweetIO = "https://dweet.io/dweet/for/"
    myName = "raspPi3_prot"
    rqsString = dweetIO+myName+'?'+'Temp='+'{:.1f}'.format(temp)+'&Hum='+'{:.1f}'.format(hum)+'&WD='+'{:.2f}'.format(WD)+'&RIS1='+'{:.6f}'.format(RIS1)+'&RIS2='+'{:.6f}'.format(RIS2)+'&RIS3='+'{:.6f}'.format(RIS3)+'&SEV1='+'{:.6f}'.format(SEV1)+'&SEV2='+'{:.6f}'.format(SEV2)+'&SEV3='+'{:.6f}'.format(SEV3)
    rqs = requests.get(rqsString)
    print(rqs.status_code)
    print(rqs.headers)
    print(rqs.content)
except Exception as e:
    print("Can't connect to dweet.io data storage, check your internet connection.")
    pass

# Datalogging
# Need to truncate numbers for table order
temp,hum,WD,wd,wet,index,CISOdia = '{:.1f}'.format(temp),'{:.1f}'.format(hum),'{:.2f}'.format(WD),'{:.2f}'.format(wd),'{:.2f}'.format(wet),'{:.4f}'.format(index),'{:.4f}'.format(CISOdia)
SPORn,RIS1,RIS2,RIS3,SEV1,SEV2,SEV3 = '{:.4f}'.format(SPORn),'{:.6f}'.format(RIS1),'{:.6f}'.format(RIS2),'{:.6f}'.format(RIS3),'{:.6f}'.format(SEV1),'{:.6f}'.format(SEV2),'{:.6f}'.format(SEV3)
tdet,tdet2,thum,t,tstop = '{:.0f}'.format(tdet),'{:.0f}'.format(tdet2),'{:.0f}'.format(thum),'{:.0f}'.format(t),'{:.0f}'.format(tstop)
w.writerow([hract[0:19],temp,hum,WD,wd,wet,index,degree2,CISOdia,SPORn,RIS1,RIS2,RIS3,SEV1,SEV2,SEV3,tdet,tdet2,thum,t,tstop])
ap_data.close()

# Closing
GP.cleanup()
print('Fin del código.')

