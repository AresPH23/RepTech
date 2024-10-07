import RPi.GPIO as GPIO
import tkinter as tk

# Configuración de la Raspberry Pi
GPIO.setmode(GPIO.BCM)
PWM_PIN = 18  # Pin GPIO donde se genera la señal PWM
GPIO.setup(PWM_PIN, GPIO.OUT)

# Inicialización del PWM en el pin seleccionado con una frecuencia de 1 kHz
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)  # Inicialmente con un ciclo de trabajo de 0%

def update_pwm(duty_cycle):
    """Actualiza el ciclo de trabajo del PWM."""
    pwm.ChangeDutyCycle(duty_cycle)

# Configuración de la interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Control de PWM")

# Etiqueta para mostrar el ciclo de trabajo actual
duty_label = tk.Label(root, text="Ciclo de trabajo: 0%")
duty_label.pack()

# Barra deslizante para ajustar el ciclo de trabajo
duty_scale = tk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=400, command=lambda x: update_pwm(float(x)))
duty_scale.pack()

# Función para actualizar la etiqueta con el valor del ciclo de trabajo
def update_label(val):
    duty_label.config(text=f"Ciclo de trabajo: {val}%")

# Vincular la barra deslizante con la actualización de la etiqueta
duty_scale.config(command=lambda val: [update_pwm(float(val)), update_label(val)])

# Ejecutar el bucle principal de Tkinter
root.mainloop()

# Limpiar la configuración de GPIO al cerrar la aplicación
GPIO.cleanup()
