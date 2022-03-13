import machine, sdcard, os, CCS811, time, urequests, gc
from machine import SoftI2C, Pin
from machine import ADC
from bmp280 import *
from mpu9250 import MPU9250

request = None
a = None
g = None
m = None
sd = None
sdDir = None
line = None

def sht20_temperature():
    i2c.writeto(0x40,b'\xf3')
    time.sleep_ms(70)
    t=i2c.readfrom(0x40, 2)
    return -46.86+175.72*(t[0]*256+t[1])/65535

def sht20_humidity():
    i2c.writeto(0x40,b'\xf5')
    time.sleep_ms(70)
    t=i2c.readfrom(0x40, 2)
    return -6+125*(t[0]*256+t[1])/65535

def sendPost(data):
    request = urequests.post('http://ptsv2.com/t/sollarium-post-test/post', json=data)
    print("")
    print("sendPost"+str(data))
    print("HTTP Status: " + str(request.status_code))
    print("HTTP Response: " + str(str(request.content)))
    gc.collect()
    
def sendCsvSd(data, url):
    print("fileData:"+data)
    file=open("/sd/SollariumTest{}.csv".format(url), "ba")
    file.write("Temperatura: 34; Umidade: 20;")
    file.write("\n")
    file.close()
    gc.collect()
    
#sd card initialization
sd = sdcard.SDCard(machine.SPI(1, sck=machine.Pin(18), mosi=machine.Pin(23), miso=machine.Pin(19)), machine.Pin(15))
os.mount(sd, "/sd")
os.listdir("/sd")
sdDir=os.listdir("/sd")

#luminosity sensor initialization
adc34=ADC(Pin(34))
adc34.atten(ADC.ATTN_11DB)
adc34.width(ADC.WIDTH_12BIT)

#battery sensor initialization
adc35=ADC(Pin(35))
adc35.atten(ADC.ATTN_11DB)
adc35.width(ADC.WIDTH_12BIT)

i2c=SoftI2C(scl=Pin(22), sda=Pin(21))
bus=SoftI2C(scl=Pin(22), sda=Pin(21))
#CCS811 initialization
sCCS811=CCS811.CCS811(i2c=bus, addr=90)
#bmp280 initialization
bmp280=BMP280(bus)
bmp280.use_case(BMP280_CASE_WEATHER)
bmp280.oversample(BMP280_OS_HIGH)
#mpu9250s initialization
mpu9250s=MPU9250(i2c)

while True:
    temperature=sht20_temperature()
    humidity=sht20_humidity()
    luminosity=adc34.read()
    if sCCS811.data_ready():
        co2=sCCS811.eCO2
    bmp280.normal_measure()
    pressure=bmp280.pressure
    bmp280temp=bmp280.temperature
    bmp280.sleep()
    a=mpu9250s.acceleration #acelerometer
    g=mpu9250s.gyro #gyroscope
    m=mpu9250s.magnetic #magnetometer
    ax=a[0]
    ay=a[1]
    az=a[2]
    gx=g[0]
    gy=g[1]
    gz=g[2]
    mx=m[0]
    my=m[1]
    mz=m[2]
    battery=adc35.read()
    
    lineData = "Temperature: "+str(temperature)+"; "
    #lineData += "Humidity: "+str(humidity)+"; "
    #lineData += "Luminosity: "+str(luminosity)+"; "
    #lineData += "Pressure: "+str(pressure)+"; "
    #lineData += "AcelX: "+str(a[0])+"; "
    #lineData += "AcelY: "+str(a[1])+"; "
    #lineData += "AcelZ: "+str(a[2])+"; "
    #lineData += "GyroX: "+str(g[0])+"; "
    #lineData += "GyroY: "+str(g[1])+"; "
    #lineData += "GyroZ: "+str(g[2])+"; "
    #lineData += "MagX: "+str(m[0])+"; "
    #lineData += "MagY: "+str(m[1])+"; "
    #lineData += "MagZ: "+str(m[2])+"; "
    #lineData += "Battery: "+str(battery)+"; "
    
    jsonData = {
        "t":temperature, #temperature sht20
        "h":humidity, #humidity sht20
        "l":luminosity,
        "p":pressure, #pressure bmt280
        "a":a, #acelerometer (x, y, z) mpu9250
        "g":g, #gyroscope (x, y, z) mpu9250
        "m":m, #magnetometer (x, y, z) mpu9250
        "b":battery, #battery level sensor
    }
    
    sendPost(jsonData)
    sendCsvSd(lineData, len(sdDir))
    time.sleep(4)
    