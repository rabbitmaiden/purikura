#!/usr/bin/python
import picamera
import time
import pygame

#colors
white = pygame.Color(255,255,255)
pygame.init();
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
camera = picamera.PiCamera();
camera.resolution = (600,800)


def attractMode():
	screen.fill(white)
	pygame.display.update()

	# Touch to start


	while 1:
		# listen for button press
		echo "press a button!"
		time.sleep(10)

def photoMode():

	# Create directory for photos

	# Take 4 photos
	for i in range(1,5):
		takePhoto(i)

	# Upload photos to server


	# Direct to drawing side


	# go back to attract mode
	attractMode()

def takePhoto(number):
	filename = number + ".jpg"

	# Show suggested pose


	#window: (x, y, width, height)
	options = {'fullscreen':False, 'window': (100,100,100,100)}
	camera.start_preview(**options)


	time.sleep(10)

	# countdown from 3


	# stop preview

	photoOptions = {'quality':95}
	camera.capture("test.jpg", "jpeg", **photoOptions)

	# chroma key???

	# display photo on screen



if __name__ == "__main__":
	attractMode()