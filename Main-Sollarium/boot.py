# Sollarium Cubesat boot
import network
ssid= 'DBUG_LUCAS_KLEAL'
password = 'lucaskleal222'
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)
while wifi.isconnected() == False:
    pass
print("Connected to {}".format(ssid))
print(wifi.ifconfig())