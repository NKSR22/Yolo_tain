from gpiozero import DigitalInputDevice
from signal import pause
from config import SENSOR_PIN

sensor = DigitalInputDevice(SENSOR_PIN)
sensor.when_activated = lambda: print("Object detected!")
sensor.when_deactivated = lambda: print("Object cleared.")

print("Waiting for sensor events... (Ctrl+C to stop)")
pause()
