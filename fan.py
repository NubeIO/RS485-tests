import RPi.GPIO as GPIO
import time

# Setup
GPIO.setmode(GPIO.BCM)  # Use Broadcom pin numbering
GPIO.setup(19, GPIO.OUT)  # Set GPIO19 as an output

# Create a PWM instance on GPIO19 at 100 Hz
fan = GPIO.PWM(19, 100)

# Start PWM with 0% duty cycle (fan off)
fan.start(0)

try:
    fan.ChangeDutyCycle(100)
    while True:
        # Increase speed
        time.sleep(1)

        # # Decrease speed
        # for duty_cycle in range(100, -1, -10):
        #     fan.ChangeDutyCycle(duty_cycle)
        #     time.sleep(1)

except KeyboardInterrupt:
    # Graceful exit on CTRL+C
    pass

# Stop PWM
fan.stop()

# Cleanup
GPIO.cleanup()
