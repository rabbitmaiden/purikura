#!/usr/bin/python
import picamera
import time

camera = picamera.PiCamera();
camera.resolution = (600,800)

camera.start_preview();

time.sleep(5)

camera.capture("chromakey.jpg", format="jpeg", quality=95)