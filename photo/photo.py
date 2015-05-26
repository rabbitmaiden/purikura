#!/usr/bin/python
import picamera
import time
import sys
import pygame
from pygame import mixer
import RPi.GPIO as GPIO
import random
import os
import requests
import io
from PIL import Image
import StringIO

musicOn = True

#colors
white = pygame.Color(255,255,255)

#startup pygame
pygame.mixer.pre_init(44100, -16, 1, 2048)
pygame.init();
pygame.mouse.set_visible(False)
mixer.init(channels=2);
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

#startup the camera
camera = picamera.PiCamera();
camera.resolution = (552,736)

# force white balance
camera.awb_mode = 'off'
camera.awb_gains = (1, 2)
camera.exposure_mode="antishake"

#startup the button
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH)

# countdown images
one = pygame.image.load("images/1.png")
two = pygame.image.load("images/2.png")
three = pygame.image.load("images/3.png")

def buttonOff():
  GPIO.output(4, GPIO.LOW)

def buttonOn():
  GPIO.output(4, GPIO.HIGH)

sfx = mixer.Sound("chime.wav")
sfx.set_volume(1)

def playChime():
  sfx.play()

def playMusic():
  mixer.music.load("purikuraloop.ogg")
  mixer.music.set_volume(.2)
  mixer.music.play(-1)

def attractMode():
  buttonOn()

  #current position of graphic
  currentPosition = 0
  attractModeMoveGraphic(currentPosition)

  lastMoved = time.time()

  # Touch to start
  while True:
    # listen for button press
    input_state = GPIO.input(18)
    if (input_state == False):
      playChime()
      buttonOff()
      photoMode()
      return

    timeSinceMoved = time.time() - lastMoved
    if (timeSinceMoved > 3):
      if (currentPosition == 2):
        currentPosition = 0
      else: 
        currentPosition += 1
      attractModeMoveGraphic(currentPosition)
      lastMoved = time.time()

    checkForQuit()

attractModeImg = pygame.image.load("images/attractmode.png")

def attractModeMoveGraphic(pos):
  positions = ((100,100), (400,400), (600,200))

  # show "press button to start" graphic
  screen.fill(white)
  screen.blit(attractModeImg, positions[pos])
  pygame.display.update()

suggestedPoses = range(1,18)

def photoMode():

  # shuffle our suggested poses
  random.shuffle(suggestedPoses)

  takeFour = pygame.image.load("images/takefour.png")
  screen.fill(white);
  screen.blit(takeFour, (340, 180))
  pygame.display.update();
  wait(3)

  # Create directory for photos
  now = time.time()

  photos = []

  # Take 4 photos
  for i in range(1,5):
    photo = takePhoto(i)
    photos.append(photo)

  # Upload photos to server
  side = uploadPhotos(photos)

  playChime()

  # Direct to drawing side
  directImgFile = "images/pinkside.png"
  if (side == 'BLUE'):
    directImgFile = "images/blueside.png"

  directImg = pygame.image.load(directImgFile)

  screen.fill(white)
  screen.blit(directImg, (330, 50))
  pygame.display.update()
  wait(15)

  # go back to attract mode
  attractMode()


def oneSecondNumber(num):
  screen.fill(white)
  screen.blit(num, (190,232))
  screen.blit(num, (900,232))
  pygame.display.update()
  wait(1)
  screen.fill(white)
  pygame.display.update()

def takePhoto(number):
  suggestedPose(number)

  #window: (x, y, width, height)
  options = {'fullscreen':False, 'window': (415,0,450,720)}
  camera.start_preview(**options)
  camera.hflip = True

  wait(2)

  oneSecondNumber(three)
  oneSecondNumber(two)
  oneSecondNumber(one)

  # stop preview
  camera.stop_preview()
  stream = io.BytesIO()
  photoOptions = {'quality':95}
  camera.capture(stream, "jpeg", **photoOptions)

  stream.seek(0);
  playChime()

  pilImage = Image.open(stream)

  mode = pilImage.mode
  size = pilImage.size
  data = pilImage.tostring()

  pygameImage = pygame.image.fromstring(data, size, mode)

  # chroma key???

  # display photo on screen
  screen.fill(white)
  screen.blit(pygameImage, (400,0))
  pygame.display.update()
  wait(5)

  return pilImage

suggestedPoseText = pygame.image.load("images/suggestedpose.png")

def suggestedPose(number):
  # Show suggested pose
  screen.fill(white)

  # TODO: ALIGN THIS
  screen.blit(suggestedPoseText, (339,20))

  suggestedPoseImg = pygame.image.load("images/suggested/" + str(suggestedPoses[number-1]) + ".jpg")

  # TODO: Align this too
  screen.blit(suggestedPoseImg, (452, 150))
  pygame.display.update()

  wait(4)

  screen.fill(white)
  pygame.display.update()

def uploadPhotos(photos):

  screen.fill(white)
  loading = pygame.image.load("images/saving.png")
  screen.blit(loading, (400, 270))
  pygame.display.update()

  files = []

  for i in range(1,5):
    j = i-1;
    imgFile = StringIO.StringIO()
    photos[j].save(imgFile, "jpeg")
    imgFile.seek(0)
    files.append(('photo'+str(i), imgFile))

  params = {'action': 'photo'}
  url = 'http://192.168.1.120/'
  r = requests.post(url, files=files, params=params);
  response = r.json()

  return response['side']



def wait(seconds):
  start = time.time()
  notDone = True
  while notDone:
    now = time.time()
    elapsed = now - start
    notDone = (elapsed < seconds)
    checkForQuit()
  return

def checkForQuit():
  for event in pygame.event.get():
    if (event.type == pygame.QUIT or 
      (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
      done()

def done():
  pygame.quit()
  sys.exit()

if __name__ == "__main__":
  try:
    if musicOn:
      playMusic()
    attractMode()
  except KeyboardInterrupt:
    done()