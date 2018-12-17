# In this file are the functions corresponding to the 2nd model used for
# forecast and alert of Botrytis infection on grapevines, described by
# Broome et al. (1995), mainly used by the ENVIROCASTER system.
# The model recommends its use when the grapevines are most susceptible
# to infection, so to say, flowers and post-veraison berries.
# Parameters involved:
# temp: hourly average temperature in Celcius
# WD: leaf wetness duration in hours
# H: relative humidity

def calcIndex(temp,WD):
    tmp = temp
    wd = WD/60
    if tmp < 12:
        tmp = 12
    elif tmp > 32 and tmp < 40:
        tmp = 32
    elif tmp > 40:
        return -2.64
    if wd > 60*16:
        return 2
    index = -2.647866-0.374927*wd+0.061601*wd*tmp-0.001511*wd*tmp**2
    return index

def calcWD(tdet,time,wet,H,WD):
    if WD > 0 and wet > 9.5:
        if (time-tdet)/3600 >= 3:
            return time,0
        else:
            return tdet,WD
    if H >= 90 or wet < 9.5:
        return tdet,(time-tdet)/60
    else:
        return time,0

def degreeRisk(index):
    if index <= 0:
        return 'No'
    elif index > 0 and index <= 0.5:
        return 'Low'
    elif index > 0.5 and index <= 1:
        return 'Moderate'
    else:
        return 'High'

def raiseAlert(degree):
    if degree in ['Moderate','High']:
        print('Alert! There is a {} risk of infection!'.format(degree)+' according to Broome et al.'+'\n')
    else:
        print('There is {} risk of infection'.format(degree)+' according to Broome et.al'+'\n')





