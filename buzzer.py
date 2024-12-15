import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
scale = [262, 294, 330, 349, 392, 440, 494, 523]

try:
    p=GPIO.PWM(12, 100)
    p.start(100)
    p.ChangeDutyCycle(90)

    for i in range(1):
        p.ChangeFrequency(scale[i])
        time.sleep(1)
    p.stop()

finally:
    GPIO.cleanup()