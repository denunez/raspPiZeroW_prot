# Process Variables:
# Teq: Equivalent temperature given by the ratio (T-Tmin)/(Tmax-Tmin)
# R: mm of rain per hour per day
# WD: Duration of leaf wetness after passing a certain threshold
# H: Mean daily relative humidity
# t: Accumulated total time of humid hours during the day
# GS: Growth Stage of the flowers/fruits on grapevines
# Mf: Humid hours per day
# The functions present in this file will be used for the calculations
# involved in the mathematical model described by Elisa Gonzalez-Dominguez
# et al. (2015)

def rain():
    #!/usr/bin/python
    import smbus
    import time
    # I2C-address of YL-40
    address = 0x48
    # Create I2C instance and open the bus
    YL40 = smbus.SMBus(1)
    # Configure YL-40
    YL40.write_byte(address,0x03) # Set channel to AIN3  | = i2cset -y 1 0x48 0x03
    return YL40,address

def rain_loop(YL40,address):
    import smbus
    import time
    for i in range(3):
        rain_8bit = YL40.read_byte(address) # = i2cget -y 1 0x48
    rain = round(rain_8bit*0.064453125*1.1844131,3) # Convert 8-bit number to resistance and round
    return rain

def truncate(number,digits):
    import math
    stepper = pow(10.0,digits)
    return math.trunc(stepper*number)/stepper

def measureWD(tdet,time,wet,WD,tstop):
    if WD > 0 and wet > 9.5:
        if (time-tstop)/3600 >= 3:
            return time,0,time
        else:
            return tdet,WD,tstop
    if wet < 11.5:
        return tdet,(time-tdet)/60,time
    else:
        return time,0,time

def dayComp(dayAnt,dayDps):
    if dayAnt != dayDps:
        return True
    return False

def hourComp(hrAnt,hrDps):
    if hrAnt != hrDps:
        return True
    return False

def RP(hrAnt,hr):
    if abs((hr-hrAnt)) > 1:
        return False
    else:
        return True

def Mf(R,RP,WD,H,t,hourP,dayP):
    if t >= 23.9 or dayP:
        return 0
    if hourP:
        if t == 0:
            if (R >= 0.2 and RP) or WD >= 30 or H >= 90:
                return (t+1)/24
            else:
                return t/24
        else:
            if (R >= 0.2 and RP) or WD >= 59 or H >= 90:
                return (t+1)/24
            else:
                return t/24
    else:
        return t/24

def MYGR(Teq):
    k = (3.78*Teq**2*(1-Teq))**0.475
    return k

def SPOR(Teq,H):
    l = (3.7*Teq**0.9*(1-Teq))**10.49*(-3.595+0.097*H-0.0005*H**2)
    if l <= 0:
        return 0
    return l

def CISO(col):
    if len(col) < 7:
        return sum(col)/len(col)
    else:
        return sum(col)/7

def SUS1(GS):
    if GS < 53 or GS > 73:
        raise ValueError('GS only valid for 53 <= GS <= 73')
    else:
        m = 75.209-390.33*(GS/100)+671.25*(GS/100)**2-379.09*(GS/100)**3
        return m

def INF1(Teq,WD,GS):   # WD as minutes instead of hrs.
    from math import exp
    wd = WD/60
    n = SUS1(GS)*(3.56*Teq**0.99*(1-Teq))**0.71/(1+exp(1.85-0.19*wd))
    return n

def RIS1(CISOsem,Teq,WD,GS):
    return CISOsem*INF1(Teq,WD,GS)

def SUS2(GS):
    from math import exp
    if GS < 79 or GS > 89:
        raise ValueError('GS only valid for 79 <= GS <= 89')
    else:
        o = 5*10**(-17)*exp(0.4219*GS)
    return o

def INF2(Teq,WD,GS):    # WD as minutes instead of hrs.
    from math import exp
    wd = WD/60
    p = SUS2(GS)*(6.416*Teq**1.292*(1-Teq))**0.469*exp(-2.3*exp(-0.048*wd))
    return p

def RIS2(CISOsem,Teq,WD,GS):
    return CISOsem*INF2(Teq,WD,GS)

def SUS3(GS):
    if GS < 79 or GS > 89:
        raise ValueError('GS only valid for 79 <= GS <= 89')
    else:
        q = 0.0546*GS-3.87
    if q > 1:
        return 1
    else:
        return q

def INF3(Teq,H,GS):
    from math import exp
    r = SUS3(GS)*(7.75*Teq**2.14*(1-Teq))**0.469/(1+exp(35.36-40.26*H/100))
    return r

def RIS3(Teq,H,GS):
    return MYGR(Teq)*INF3(Teq,H,GS)

def SEV(col):
    return sum(col)

def degreeRisk(RIS):


    return 1


def raiseAlert(RIS):



    return 1

