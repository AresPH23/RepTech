import smbus2
import tkinter as tk
import RPi.GPIO as GPIO

# Configuración del DAC MCP4725
DAC_ADDRESS = 0x60  # Dirección del DAC
bus = smbus2.SMBus(1)

def set_dac_output(voltage):
    """Establece la salida del DAC a un valor de voltaje específico."""
    try:
        # Convertir el voltaje a un valor de 12 bits
        value = int(voltage * 4095 / 5)
        # Escribir el valor en el DAC
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

# Configuración del GPIO para PWM
GPIO.setmode(GPIO.BCM)
PWM_PIN = 18  # Pin GPIO donde se genera la señal PWM
GPIO.setup(PWM_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

def update_pwm(duty_cycle):
    """Actualiza el ciclo de trabajo del PWM."""
    pwm.ChangeDutyCycle(duty_cycle)
    print(f"Valor enviado al PWM: {int(duty_cycle)}"+"%")

def update_label(val):
    duty_label.config(text=f"Ciclo de trabajo: {val}%")

def on_closing():
    """Función para ejecutar cuando la ventana se cierra."""
    set_dac_output(0)  # Establecer el DAC a 0V
    pwm.stop()  # Detener el PWM
    GPIO.cleanup()  # Limpiar la configuración de GPIO
    bus.close()  # Cerrar el bus I2C
    root.destroy()  # Cerrar la ventana

# Configuración de la interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Control de DAC MCP4725 y PWM")

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

# Capturar el evento de cierre de la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar el bucle principal de Tkinter
root.mainloop()