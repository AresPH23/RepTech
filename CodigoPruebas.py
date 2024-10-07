import smbus2
import RPi.GPIO as GPIO
import time
import board
import adafruit_dht
from w1thermsensor import W1ThermSensor
import tkinter as tk

"""
CONEXION PINOUT:
PWM = 18
DAC = 2 y 3 (DATA y CLOCK)
DHT22 = 14
DS18B20 = 4
"""

# Dirección I2C del DAC MCP4725
DAC_ADDRESS = 0x60  # Dirección del DAC

# Inicialización del bus I2C
bus = smbus2.SMBus(1)

def set_dac_output(voltage):
    """Establece la salida del DAC a un valor de voltaje específico."""
    try:
        # Convertir el voltaje a un valor de 12 bits
        value = int(voltage * 4095 / 5)
        # Escribir el valor en el DAC
        bus.write_i2c_block_data(DAC_ADDRESS, 0x40, [(value >> 4) & 0xFF, (value & 0xF) << 4])
        print(f"El valor de voltaje enviado a la DAC es: {voltage} V")
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

# Configuración del GPIO para PWM
GPIO.setmode(GPIO.BCM)
PWM_PIN = 18  # Pin GPIO donde se genera la señal PWM
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

def update_pwm(duty_cycle):
    """Actualiza el ciclo de trabajo del PWM."""
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Valor enviado al PWM: {int(duty_cycle)}%")

def update_label(val):
    duty_label.config(text=f"Ciclo de trabajo: {val}%")

def on_closing():
    """Función para ejecutar cuando la ventana se cierra."""
    print("Cerrando aplicacion")
    set_dac_output(0)  # Establecer el DAC a 0V
    pwm.stop()  # Detener el PWM
    GPIO.cleanup()  # Limpiar la configuración de GPIO
    bus.close()  # Cerrar el bus I2C
    root.destroy()  # Cerrar la ventana

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
root.title("Control de DAC, PWM y Lectura de Sensores")

# Sección para el control del DAC MCP4725
voltage_label = tk.Label(root, text="DAC: 0.0 V")
voltage_label.pack()
digital_label = tk.Label(root, text="Valor Digital: 0 (12 bits)")
digital_label.pack()
percentage_label = tk.Label(root, text="Porcentaje: 0.00 %")
percentage_label.pack()
dac_scale = tk.Scale(root, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400,
                     command=lambda value: update_dac(float(value)))
dac_scale.pack()

# Sección para el control del PWM
duty_label = tk.Label(root, text="Ciclo de trabajo: 0%")
duty_label.pack()
duty_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=400,
                      command=lambda val: [update_pwm(float(val)), update_label(val)])
duty_scale.pack()

# Sección para la lectura de sensores
dht22_label = tk.Label(root, text="DHT22 - Temperatura: --C  Humedad: --%", font=("Helvetica", 16))
dht22_label.pack(pady=10)
ds18b20_label = tk.Label(root, text="DS18B20 - Temperatura: --C", font=("Helvetica", 16))
ds18b20_label.pack(pady=10)

# Iniciar la actualización de lecturas
update_readings()

# Capturar el evento de cierre de la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar el bucle principal de Tkinter
root.mainloop()
