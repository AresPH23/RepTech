from w1thermsensor import W1ThermSensor
import time

sensor = W1ThermSensor()

try:
    while True:
        temeperature = sensor.get_temperature()

        print(f"La temperature es: {temeperature:.2f}°C")
        time.sleep(3)

except KeyboardInterrupt:
    print("Lectura detenida.")

