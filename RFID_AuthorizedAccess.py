#!/usr/bin/env python
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
from mfrc522 import SimpleMFRC522
import time
GPIO.setmode(GPIO.BOARD)

# setup RFID & Servo
reader = SimpleMFRC522()
buzzer = 8
greenLed = 16
redLed = 18
servoPINlock = 10
GPIO.setup(buzzer,GPIO.OUT)
GPIO.setup(greenLed,GPIO.OUT)
GPIO.setup(redLed,GPIO.OUT)
GPIO.setup(servoPINlock,GPIO.OUT)
pLock = GPIO.PWM(servoPINlock, 50)
pLock.start(7.5)
pLock.ChangeDutyCycle(0)

print("Scan your Tag")

while True:
    id = reader.read()
    
    if 109713135970 in id:
        print("Authorized Access")
        GPIO.output(greenLed,GPIO.HIGH)
        GPIO.output(buzzer,GPIO.HIGH)
        time.sleep(0.4)
        GPIO.output(buzzer,GPIO.LOW)
        GPIO.output(greenLed,GPIO.LOW)
        time.sleep(0.2)
        pLock.ChangeDutyCycle(2.5)
        time.sleep(0.2)
        pLock.ChangeDutyCycle(0)
        time.sleep(5)
        pLock.ChangeDutyCycle(7.5)
        time.sleep(0.2)
        pLock.ChangeDutyCycle(0)
        time.sleep(5)
    else:
        print("Access Denied")
        GPIO.output(redLed,GPIO.HIGH)
        GPIO.output(buzzer,GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(redLed,GPIO.LOW)
        GPIO.output(buzzer,GPIO.LOW)
        time.sleep(0.2)
        GPIO.output(redLed,GPIO.HIGH)
        GPIO.output(buzzer,GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(redLed,GPIO.LOW)
        GPIO.output(buzzer,GPIO.LOW)
        time.sleep(0.2)
