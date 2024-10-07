import smbus2
import time

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

# Prueba de escritura de un valor de salida
xd = 0
while xd < 5:
    set_dac_output(xd)
    time.sleep(0.5)
    xd+=0.1
time.sleep(1)

set_dac_output(0)
# Cerrar el bus I2C
bus.close()
