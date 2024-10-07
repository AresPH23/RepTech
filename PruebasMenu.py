import smbus2
import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
from w1thermsensor import W1ThermSensor
import tkinter as tk
from tkinter import Toplevel
import csv
from datetime import datetime

##Configuracion DAC4725 - Puerto I2C 2 y 3
# Dirección I2C del DAC MCP4725
DAC_ADDRESS = 0x60  # Dirección del DAC
# Inicialización del bus I2C
bus = smbus2.SMBus(1)

#Configuracion DHT22 - Puerto D14


# Inicializar el sensor DHT22
dht_device = adafruit_dht.DHT22(board.D14)

# Inicializar el sensor DS18B20
ds18b20_sensor = W1ThermSensor()

# Variables para almacenar las lecturas
temperature_data = []
humidity_data = []

# Variables para el control de muestreo
sample_interval = 2000  # Intervalo en milisegundos (por defecto 2 segundos)
sample_counter = 0
is_sampling = False  # Estado del muestreo automático

def set_dac_output(voltage):
    """Establece la salida del DAC a un valor de voltaje específico."""
    try:
        value = int(voltage * 4095 / 5)
        bus.write_i2c_block_data(DAC_ADDRESS, 0x40, [(value >> 4) & 0xFF, (value & 0xF) << 4])
        print(f"Valor enviado al DAC: {value}")
        return value
    except Exception as e:
        print(f"Error al establecer la salida del DAC: {e}")
        return 0

def update_dac(voltage):
    """Actualiza el DAC con el voltaje especificado y actualiza la interfaz."""
    digital_value = set_dac_output(voltage)
    voltage_label.config(text=f"DAC: {voltage:.2f} V")
    digital_label.config(text=f"Valor Digital: {digital_value} (12 bits)")
    percentage_label.config(text=f"Porcentaje: {voltage / 5 * 100:.2f} %")


def read_dht22():
    try:
        temperature = dht_device.temperature
        humidity = dht_device.humidity
        if humidity is not None and temperature is not None:
            return temperature, humidity
        else:
            return None, None
    except RuntimeError as error:
        print(f"Error al leer el sensor DHT22: {error}")
        return None, None
    except Exception as error:
        dht_device.exit()
        raise error

def read_ds18b20():
    try:
        temperature = ds18b20_sensor.get_temperature()
        return temperature
    except Exception as error:
        print(f"Error al leer el DS18B20: {error}")
        return None

def save_csv(data, filename):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def update_readings():
    global sample_counter
    temperature, humidity = read_dht22()
    ds18b20_temperature = read_ds18b20()
    
    if temperature is not None:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        temperature_data.append([sample_counter, temperature, 'DHT22', current_time])
        humidity_data.append([sample_counter, humidity, 'DHT22', current_time])
        sample_counter += 1

        dht22_label.config(text=f'DHT22 - Temperatura: {temperature:.1f}C  Humedad: {humidity:.1f}%')
        ds18b20_label.config(text=f'DS18B20 - Temperatura: {ds18b20_temperature:.2f}C' if ds18b20_temperature is not None else 'Error al leer DS18B20')

    sensors_window.after(sample_interval, update_readings)
    if is_sampling:
        save_csv([[sample_counter, temperature, 'DHT22', current_time]], 'temperature_data.csv')
        save_csv([[sample_counter, humidity, 'DHT22', current_time]], 'humidity_data.csv')

def on_closing():
    set_dac_output(0)
    pwm.stop()
    GPIO.cleanup()
    bus.close()
    root.destroy()

def update_sample_interval(val):
    global sample_interval
    sample_interval = int(val) * 1000

def toggle_sampling():
    global is_sampling
    is_sampling = sampling_var.get()  # Obtener el estado del checkbox
    if is_sampling:
        sample_counter = 0  # Reiniciar el contador de muestras

def save_temperature_data():
    save_csv(temperature_data, 'temperature_data.csv')
    temperature_data.clear()

def save_humidity_data():
    save_csv(humidity_data, 'humidity_data.csv')
    humidity_data.clear()

# Configuración del GPIO para PWM
GPIO.setmode(GPIO.BCM)
PWM_PIN = 18
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

def update_pwm(duty_cycle):
    pwm.ChangeDutyCycle(duty_cycle)

def update_label(val):
    duty_label.config(text=f"Ciclo de trabajo: {val}%")

def open_dac_window():
    global voltage_label, digital_label, percentage_label
    dac_window = Toplevel(root)
    dac_window.title("Control de DAC MCP4725")

    voltage_label = tk.Label(dac_window, text="DAC: 0.0 V")
    voltage_label.pack()
    digital_label = tk.Label(dac_window, text="Valor Digital: 0 (12 bits)")
    digital_label.pack()
    percentage_label = tk.Label(dac_window, text="Porcentaje: 0.00 %")
    percentage_label.pack()

    dac_scale = tk.Scale(dac_window, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400,
                         command=lambda value: update_dac(float(value)))
    dac_scale.pack()

def open_pwm_window():
    global duty_label
    pwm_window = Toplevel(root)
    pwm_window.title("Control de PWM")

    duty_label = tk.Label(pwm_window, text="Ciclo de trabajo: 0%")
    duty_label.pack()
    duty_scale = tk.Scale(pwm_window, from_=0, to=100, orient=tk.HORIZONTAL, length=400,
                          command=lambda val: [update_pwm(float(val)), update_label(val)])
    duty_scale.pack()

def open_sensors_window():
    global dht22_label, ds18b20_label, sensors_window, interval_scale, sampling_var
    sensors_window = Toplevel(root)
    sensors_window.title("Lectura de Sensores")

    dht22_label = tk.Label(sensors_window, text="DHT22 - Temperatura: --C  Humedad: --%", font=("Helvetica", 16))
    dht22_label.pack(pady=10)
    ds18b20_label = tk.Label(sensors_window, text="DS18B20 - Temperatura: --C", font=("Helvetica", 16))
    ds18b20_label.pack(pady=10)

    interval_label = tk.Label(sensors_window, text="Intervalo de muestreo (segundos):")
    interval_label.pack(pady=10)
    interval_scale = tk.Scale(sensors_window, from_=1, to=60, orient=tk.HORIZONTAL, length=400, 
                              command=update_sample_interval)
    interval_scale.set(sample_interval // 1000)
    interval_scale.pack()

    sampling_var = tk.BooleanVar()
    sampling_checkbox = tk.Checkbutton(sensors_window, text="Activar muestreo automático", variable=sampling_var, command=toggle_sampling)
    sampling_checkbox.pack(pady=10)

    save_temp_button = tk.Button(sensors_window, text="Guardar Temperatura", command=save_temperature_data)
    save_temp_button.pack(pady=10)
    
    save_humidity_button = tk.Button(sensors_window, text="Guardar Humedad", command=save_humidity_data)
    save_humidity_button.pack(pady=10)

    update_readings()

# Crear la ventana principal
root = tk.Tk()
root.title("Menú Principal")

# Botones para abrir las diferentes ventanas
tk.Button(root, text="Control de DAC MCP4725", command=open_dac_window).pack(pady=10)
tk.Button(root, text="Control de PWM", command=open_pwm_window).pack(pady=10)
tk.Button(root, text="Lectura de Sensores", command=open_sensors_window).pack(pady=10)
tk.Button(root, text="Cerrar", command=on_closing).pack(pady=10)

# Capturar el evento de cierre de la ventana principal
root.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar el bucle principal de Tkinter
root.mainloop()

# Limpiar la configuración de GPIO al cerrar la aplicación
pwm.stop()
GPIO.cleanup()
