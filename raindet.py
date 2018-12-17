import RPi.GPIO as GPIO
import csv
from datetime import datetime
GPIO.setmode(GPIO.BCM)

# GPIO 27 set up as input. It is pulled up to stop false signals
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Setup of datalog of rain based on time and amount in mm
a = []
try:
    prev_data = open('rainlog.csv','r')
    r = csv.reader(prev_data,delimiter=',')
except IOError:
    new_data = open('rainlog.csv','w')
    f = csv.writer(new_data)
    h = ['UTS','Rain']
    f.writerow(h)
    x0 = [datetime.now(),0]
    f.writerow(x0)
    new_data.close()
    prev_data = open('rainlog.csv','r')
    r = csv.reader(prev_data,delimiter=',')
for row in r:
    a.append(row)
prev_data.close()

t = datetime.now()
apc = 0.2794                     # Rain in mm per bucket discharge
lluvia = float(a[-1][1])
count = 0
while True:
    ap_data = open('rainlog.csv','a')
    w = csv.writer(ap_data)
    try:
        print(str(t))
        print("Waiting for falling edge on PIN 27...")
        GPIO.wait_for_edge(27, GPIO.FALLING)
        print("\nFalling edge detected. Now your program can continue with")
        print("whatever was waiting for a button press.")
        t = str(datetime.now())
        prevDay = float(a[-1][0][8:10])
        currDay = float(t[8:10])
        print(prevDay)
        print(currDay)
        count += 1
        if prevDay == currDay:
            lluvia += apc
        else:
            lluvia = 0
        w.writerow([t,lluvia])
        ap_data.close()
    except KeyboardInterrupt:
        break
try:
    ap_data.close()
except:
    GPIO.cleanup()
GPIO.cleanup()           # clean up GPIO on normal exit
