import time
import board
import adafruit_dht

# Define el tipo de sensor y el pin GPIO al que está conectado
sensor = adafruit_dht.DHT22(board.D14)

while True:
    try:
        # Intenta leer la temperatura y la humedad del sensor
        temperatura = sensor.temperature
        humedad = sensor.humidity
        
        # Verifica si la lectura fue exitosa
        if humedad is not None and temperatura is not None:
            print(f'Temperatura: {temperatura:.2f}°C')
            print(f'Humedad: {humedad:.2f}%')
        else:
            print('Error al leer del sensor DHT22. Verifica las conexiones.')
        
        # Espera 2 segundos antes de la siguiente lectura
        time.sleep(3)

    except RuntimeError as error:
        # Errores ocasionales de lectura son normales
        print(f'Error al leer el sensor: {error.args[0]}')
        time.sleep(2)
    except Exception as error:
        sensor.exit()
        raise error
