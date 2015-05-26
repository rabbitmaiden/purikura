#!/usr/bin/python

import picamera
import pygame
import time
import io
import RPi.GPIO as GPIO
from PIL import Image

white = pygame.Color(255,255,255)

pygame.init()

pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

screen.fill(white)
pygame.display.update()


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


camera = picamera.PiCamera();
camera.resolution = (552,736)
camera.awb_mode = 'fluorescent'

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)
options = {'fullscreen':False, 'window': (415,0,450,720)}
camera.start_preview(**options)
camera.hflip = True


def checkForQuit():
  for event in pygame.event.get():
    if (event.type == pygame.QUIT or 
      (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
      done()

def oneSecondNumber(num):
  screen.fill(white)
  screen.blit(num, (190,232))
  screen.blit(num, (900,232))
  pygame.display.update()
  time.sleep(3)
  screen.fill(white)
  pygame.display.update()


one = pygame.image.load("images/1.png");
two = pygame.image.load("images/2.png");
three = pygame.image.load("images/3.png")

while True:
  input_state = GPIO.input(18)
  if input_state == False:

    oneSecondNumber(three)
    oneSecondNumber(two)
    oneSecondNumber(one)

    stream = io.BytesIO()
    camera.capture(stream, "jpeg", quality=95)
    camera.stop_preview()
    stream.seek(0);
    pilImage = Image.open(stream);

    mode = pilImage.mode
    size = pilImage.size
    data = pilImage.tostring()

    pygameImage = pygame.image.fromstring(data, size, mode)

    screen.fill(white)
    screen.blit(pygameImage, (0, 0))
    pygame.display.update()


    time.sleep(10)
    screen.fill(white)
    pygame.display.update()
    camera.start_preview()
  checkForQuit()
