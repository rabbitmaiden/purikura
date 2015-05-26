import pygame
from pygame import mixer
import time
import RPi.GPIO as GPIO

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)

pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()

mixer.init(channels=2)
mixer.music.load("purikuraloop.ogg")
mixer.music.set_volume(.2)
mixer.music.play(-1)


print "music should be playing"

sfx = mixer.Sound("chime.wav")
sfx.set_volume(1)

while 1:
  input_state = GPIO.input(18)
  if input_state == False:
  	 print "chime"
  	sfx.play()

  	time.sleep(5)
