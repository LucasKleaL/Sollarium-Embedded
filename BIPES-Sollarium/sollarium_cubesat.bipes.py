from machine import I2C, Pinimport CCS811import timefrom bmp280 import *from mpu9250 import MPU9250from machine import ADCfrom machine import Pinimport timeimport networka = Noneg = Nonem = Nonedef sht20_temperature():    i2c.writeto(0x40,b'\xf3')    time.sleep_ms(70)    t=i2c.readfrom(0x40, 2)    return -46.86+175.72*(t[0]*256+t[1])/65535def sht20_humidity():    i2c.writeto(0x40,b'\xf5')    time.sleep_ms(70)    t=i2c.readfrom(0x40, 2)    return -6+125*(t[0]*256+t[1])/65535adc34=ADC(Pin(34))adc34.atten(ADC.ATTN_11DB)adc34.width(ADC.WIDTH_12BIT)adc35=ADC(Pin(35))adc35.atten(ADC.ATTN_11DB)adc35.width(ADC.WIDTH_12BIT)sta_if = network.WLAN(network.STA_IF)sta_if.active(True)# Describe this function...def setWifi():  global a, g, m  sta_if = network.WLAN(network.STA_IF); sta_if.active(True)  sta_if.scan()  sta_if.connect('DBUG_LUCAS_KLEAL','lucaskleal222')  print("Waiting for Wifi connection")  while not sta_if.isconnected(): time.sleep(1)  print("Connected")  print(sta_if.ifconfig())#Code automatically generated by BIPES (http://www.bipes.net.br)#Author: 'Lucas Kusman Leal'#IOT ID: 0#Description: 'Sollarium cubesat'bus=I2C(scl=Pin(22), sda=Pin(21))sCCS811 = CCS811.CCS811(i2c=bus, addr=90)i2c=I2C(scl=Pin(22), sda=Pin(21))bus=I2C(scl=Pin(22), sda=Pin(21))bmp280 = BMP280(bus)bmp280.use_case(BMP280_CASE_WEATHER)bmp280.oversample(BMP280_OS_HIGH)i2c=I2C(scl=Pin(22), sda=Pin(21))mpu9250s = MPU9250(i2c)setWifi()while True:  print('')  print('Temperatura: ' + str(sht20_temperature()))  print('Umidade: ' + str(sht20_humidity()))  print('Luminosidade: ' + str(adc34.read()))  if sCCS811.data_ready():    print('CO2: ')    print(sCCS811.eCO2)    print(sCCS811.tVOC)  bmp280.normal_measure()  print(''.join([str(x) for x in ['Presso: ', bmp280.pressure, ', Temperatura: ', bmp280.temperature]]))  bmp280.sleep()  a = mpu9250s.acceleration  g = mpu9250s.gyro  m = mpu9250s.magnetic  print('A: ' + str(a))  print('Ax: ' + str(a[0]))  print('Ay: ' + str(a[1]))  print('Az: ' + str(a[2]))  print('Gx: ' + str(g[0]))  print('Gy: ' + str(g[1]))  print('Gz: ' + str(g[2]))  print('Mx: ' + str(m[0]))  print('My: ' + str(m[1]))  print('Mz: ' + str(m[2]))  print('T: ' + str(mpu9250s.temperature))  print('Bateria: ' + str(adc35.read()))  print('$BIPES-DATA:',1,',',a[0])  time.sleep(4)