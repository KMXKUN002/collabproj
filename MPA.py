#!/usr/bin/python3
"""
Python Practical Template
Keegan Crankshaw
Readjust this Docstring as follows:
Names: Aluwani Malalamabi, Chris Kim
Student Number: MLLALU001, KMXKUN002
Prac: Mini-project
Date: <15/10/2019>
"""

# import Relevant Librares
import RPi.GPIO as GPIO
import smbus
import spidev
import time
import blynklib



#setup SPI
bus = 0
device = 0
spi = spidev.SpiDev()
spi.open(bus,device)
spi.max_speed_hz = 500000
spi.mode = 0

#setup I2C
REMEMBER = smbus.SMBus(1)
addr = 0x6F

#variable initialisations
systemStart = time.time()
timeSinceAlarm = 0
monitoring = True
monitorFrequency = 0
freqArray = [1, 2, 5]
alarmPlaying = False

#Constants to send to blynk
humidity = 0
temperature = 0
light = 0
systemTime = ''
customVoltage = 0


#Connect to blynk
BLYNK_AUTH = 'bTm3BTK7nTR2Bwk5kKSEt5uNtv5EjLjI'
blynk = blynklib.Blynk(BLYNK_AUTH)


def reset():
    global systemStart

    systemStart = time.time()
    
def freqInc():
    global monitorFrequency

    monitorFrequency = (monitorFrequency+1)%3   

def rtcTime():
    
    #now = datetime.now()
    
    #write_byte_data(addr, 0x02, now.hour)
    #write_byte_data(addr, 0x01, now.minute)
    #write_byte_data(addr, 0x00, now.second)

    #HH = REMEMBER.read_byte_data(addr,0x02)
    #MM = REMEMBER.read_byte_data(addr,0x01)
    #SS = REMEMBER.read_byte_data(addr,0x00)
    
    
    r = time.gmtime()
    print("RTC time | {}:{}:{}".format (r.tm_hour, r.tm_min, r.tm_sec))

def timer():
    """
    global systemHours
    global systemMins
    global systemSecs

    systemSecs +=1
    if (systemSecs==60):
        systemSecs=0
        systemMins+=1
        if (systemMins==60):
            systemMins=0
            systemHours+=1
    
    print("Sys Timer| {}:{}:{}".format(systemHours,systemMins,systemSecs))
    """
    
    global systemStart, systemTime
    
    t = time.localtime(time.time() - systemStart - 2)
    systemTime = "{}:{}:{}".format (t.tm_hour, t.tm_min, t.tm_sec)


def alarm():
    global timeSinceAlarm, alarmPlaying, systemStart
    if (alarmPlaying):
        print ("!!!!!! Alarm on !!!!!!")

    age = time.time() - systemStart
    
    dacReading = dacOut()
    if (dacReading > 2.65 or dacReading < 0.65):
        if (age - timeSinceAlarm > 180 or timeSinceAlarm == 0 or age < timeSinceAlarm):
            GPIO.output (6, True)
            alarmPlaying = True


def dismissAlarm():
    global timeSinceAlarm, alarmPlaying, systemStart
    GPIO.output (6, False)
    alarmPlaying = False
    timeSinceAlarm = time.time() - systemStart


#read data from the adc
def ReadChan(channel):
    global spi

    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def voltConvert(data,places):
    voltage = (data*3.3)/float(1023)
    voltage = round (voltage,places)
    return voltage

def temperature():
    global temperature
    
    temp = voltConvert (ReadChan(1), 2)
    temp = (temp-float(0.5))*float(100)
    temperature = temp

def lightSen():
    global light
    light = ReadChan(0)

def humiditySen():
    global humidity
    humidity = voltConvert(ReadChan(2), 2)

def dacOut():
    global light, humidity, customVoltage
    
    customVoltage = round ((light/float(1023))*humidity, 2)
    
def startStop():
    global monitoring
    if monitoring:
        monitoring = False
    else:
        monitoring = True
    
def initGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    #setup of pins
    GPIO.setup(6,GPIO.OUT)
    GPIO.output(6,False)
    GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(27,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(23, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)

    
    #button interrupts
    GPIO.add_event_detect(17,GPIO.BOTH,callback=reset,bouncetime = 200)
    GPIO.add_event_detect(27,GPIO.BOTH,callback=freqInc,bouncetime = 200)
    GPIO.add_event_detect(22,GPIO.BOTH,callback=dismissAlarm,bouncetime = 200)
    GPIO.add_event_detect(23,GPIO.BOTH,callback=startStop,bouncetime = 200)


def main():
    global systemStart
    global spi
    global monitoring
    global monitorFrequency, freqArray
    global systemTime, light, humidity, temperature, customVoltage
    
    initGPIO()
 
    while monitoring: 
        print("______________________")
        alarm()
        rtcTime()
        timer()
        lightSen()
        humiditySen()
        temperature()
        dacOut()
        
        print("Sys Timer| {}".format(systemTime))
        print("Light    | {}".format(light))
        print("Humidity | {}".format(humidity))
        print("Temp     | {}".format(temperature))
        print("DAC Out  | {}".format(customVoltage))

        time.sleep (freqArray[monitorFrequency])
        
        
@blynk.handle_event('read V3')
def read_virtual_pin_handler(pin):
    global humidity, temperature, light, systemTime, customVoltage

    blynk.virtual_write (3, '{}:{}:{}'.format(systemTime))
    blynk.virtual_write (2, light)
    blynk.virtual_write (1, '{} C'.format(temperature))
    blynk.virtual_write (0, humidity)
    blynk.virtual_write (4, customVoltage)
        
        
if __name__ == "__main__":
    # Make sure the GPIO is stopped correctly
    try:
        while True:
            main()
    except KeyboardInterrupt:
        print("Exiting gracefully")
        # Turn off your GPIOs here
        GPIO.cleanup()
    except Exception as e:
        GPIO.cleanup()
        print("Some other error occurred")
        print(e.message)

while True:
    blynk.run()