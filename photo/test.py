import io
import time
import picamera
import cv2
import numpy as np



# "Decode" the image from the array, preserving colour
image = cv2.imread("chromakey.jpg")

pMOG = cv2.BackgroundSubtractorMOG()

fgmask = pMOG.apply(image)
cv2.imwrite("pmog.jpg", fgmask)