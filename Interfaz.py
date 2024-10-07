import time
import board
import adafruit_dht
from w1thermsensor import W1ThermSensor

#Definir entradas de los sensores
Sensor_DHT = adafruit_dht.DHT22(board.D14) 

