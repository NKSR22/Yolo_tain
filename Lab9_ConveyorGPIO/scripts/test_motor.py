from gpiozero import Motor
from time import sleep
from config import MOTOR_IN1, MOTOR_IN2, MOTOR_ENABLE

motor = Motor(forward=MOTOR_IN1, backward=MOTOR_IN2, enable=MOTOR_ENABLE)

print("Running conveyor forward for 3 seconds...")
motor.forward()
sleep(3)
motor.stop()
print("Motor test done.")
