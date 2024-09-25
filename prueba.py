import time
import board
import adafruit_dht
from w1thermsensor import W1ThermSensor
import tkinter as tk

# Inicializar el sensor DHT22
dht_device = adafruit_dht.DHT22(board.D14)

# Inicializar el sensor DS18B20
ds18b20_sensor = W1ThermSensor()

def read_dht22():
    try:
        # Obtener la temperatura y la humedad del DHT22
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if humidity is not None and temperature is not None:
            return f'DHT22 - Temperatura: {temperature:.1f}C  Humedad: {humidity:.1f}%'
        else:
            return 'Error al leer el sensor DHT22'
    except RuntimeError as error:
        return error.args[0]
    except Exception as error:
        dht_device.exit()
        raise error

def read_ds18b20():
    try:
        # Obtener la temperatura del DS18B20
        temperature = ds18b20_sensor.get_temperature()
        return f'DS18B20 - Temperatura: {temperature:.2f}C'
    except Exception as error:
        return f'Error al leer el DS18B20: {error}'

def update_readings():
    dht22_reading = read_dht22()
    ds18b20_reading = read_ds18b20()
    dht22_label.config(text=dht22_reading)
    ds18b20_label.config(text=ds18b20_reading)
    root.after(2000, update_readings)  # Actualiza cada 2 segundos

# Crear la ventana principal
root = tk.Tk()
root.title("Lectura de Sensores")

# Crear etiquetas para mostrar las lecturas
dht22_label = tk.Label(root, text="DHT22 - Temperatura: --C  Humedad: --%", font=("Helvetica", 16))
dht22_label.pack(pady=10)

ds18b20_label = tk.Label(root, text="DS18B20 - Temperatura: --C", font=("Helvetica", 16))
ds18b20_label.pack(pady=10)

# Iniciar la actualización de lecturas
update_readings()

# Ejecutar el bucle principal de la aplicación
root.mainloop()
