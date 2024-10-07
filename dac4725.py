import smbus2
import tkinter as tk

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
        print(f"Valor enviado al DAC: {value}")
    except Exception as e:
        print(f"Error al establecer la salida del DAC: {e}")

def update_dac(voltage):
    """Actualiza el DAC con el voltaje especificado y actualiza la interfaz."""
    digital_value = set_dac_output(voltage)  # Llama a la función que establece el DAC
    voltage_label.config(text=f"DAC: {voltage:.2f} V")  # Actualiza la etiqueta de voltaje
    digital_label.config(text=f"Valor Digital: {int(voltage * 4095 / 5)} ")  # Actualiza la etiqueta de valor digital
    percentage_label.config(text=f"Porcentaje: {voltage / 5 * 100:.2f} %")  # Actualiza la etiqueta de porcentaje

def on_closing():
    """Función para ejecutar cuando la ventana se cierra."""
    set_dac_output(0)  # Establecer el DAC a 0V
    bus.close()  # Cerrar el bus I2C
    root.destroy()  # Cerrar la ventana

# Configuración de la interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Control de DAC MCP4725")

# Etiqueta para mostrar el voltaje actual del DAC
voltage_label = tk.Label(root, text="DAC: 0.0 V")
voltage_label.pack()

# Etiqueta para mostrar el valor digital del DAC
digital_label = tk.Label(root, text="Valor Digital: 0 ")
digital_label.pack()

# Etiqueta para mostrar el porcentaje
percentage_label = tk.Label(root, text="Porcentaje: 0.00 %")
percentage_label.pack()

# Barra deslizante para ajustar el voltaje de salida del DAC
dac_scale = tk.Scale(root, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL, length=400,
                     command=lambda value: update_dac(float(value)))  # Convertir a float aquí
dac_scale.pack()

# Capturar el evento de cierre de la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

# Ejecutar el bucle principal de Tkinter
root.mainloop()
