import machine, sdcard, os, CCS811, time, urequests, gc, mcp23017, json
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
    #led
    if (request.status_code == 200): #successful http post
        mcpIO.output(3, 1)
        time.sleep(1)
        mcpIO.output(3, 0)
    else: #error exception http post
        mcpIO.output(4, 1)
        time.sleep(1)
        mcpIO.output(4, 0)
    gc.collect()
    
def sendCsvSd(data, url):
    file=open("/sd/SollariumTest{}.csv".format(url), "ba")
    file.write(str(data))
    file.write("\n")
    file.close()
    gc.collect()
    
def setBatteryLevel(battery):
    maxValue = 2500
    batteryPercent = (maxValue - battery) * 100 / maxValue
    batteryLevel = 100.0 - batteryPercent
    return round(batteryLevel)
    
#sd card initialization
sd = sdcard.SDCard(machine.SPI(1, sck=machine.Pin(18), mosi=machine.Pin(23), miso=machine.Pin(19)), machine.Pin(15))
os.mount(sd, "/sd")
os.listdir("/sd")
sdDir=os.listdir("/sd")
file=open("/sd/SollariumTest{}.csv".format(len(sdDir)), "ba")
header = "Temperature; Humidity; Luminosity; Pressure; AcelX; AcelY; AcelZ; GyroX; GyroY; GyroZ; MagX; MagY; MagZ; Battery; BatteryLevel;"
file.write(str(header))
file.write("\n")
file.close()

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
#mcp23017 (leds) initialization
mcpIO = mcp23017.MCP23017()

while True:
    temperature=round(sht20_temperature(), 2)
    humidity=round(sht20_humidity(), 2)
    luminosity=adc34.read()
    if sCCS811.data_ready():
        co2=sCCS811.eCO2
    bmp280.normal_measure()
    pressure=round(bmp280.pressure)
    bmp280temp=round(bmp280.temperature, 2)
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
    batteryLevel=setBatteryLevel(battery)
    compactA = round(ax, 2), round(ay, 2), round(az, 2)
    compactG = round(gx, 2), round(gy, 2), round(gz, 2)
    compactM = round(mx, 2), round(my, 2), round(mz, 2)
    
    lineData = ("{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};"
                "{};").format(str(temperature), str(humidity), str(luminosity), str(pressure), str(ax), str(ay), str(az), str(gx), str(gy), str(gz), str(mx), str(my), str(mz), str(battery), str(batteryLevel))
    
    jsonData = {
        "t":temperature,"h":round(humidity),"p":pressure,"a":compactA,"g":compactG,"m":compactM,"bl":batteryLevel,
        #temperature sht20, humidity sht20 #pressure bmt280
        #"l":luminosity,
        #"ax": round(a[0], 2),
        #"ay": round(a[1], 2),
        #"az": round(a[2], 2),
        #"gx": round(g[0], 2),
        #"gy": round(g[1], 2),
        #"gz": round(g[2], 2),
        #"mx": round(m[0], 2),
        #"my": round(m[1], 2),
        #"mz": round(m[2], 2),
        #"b":battery, #battery raw sensor value
        #battery level percent
    }
    
    #dumpJson = json.dumps(jsonData, separators=(",", ":"))
    #print("dumpJson {}".format(dumpJson))
    #compactJsonData = json.loads(json.dumps(jsonData, separators=(",", ":")))
    
    strJsonData = str(jsonData).replace(" ","")
    dumpJson = json.dumps(strJsonData)
    compactJsonData = json.loads(dumpJson)
    
    sendPost(compactJsonData)
    print("compactJsonData {}".format(compactJsonData))
    sendCsvSd(lineData, len(sdDir))
    time.sleep(4)
    