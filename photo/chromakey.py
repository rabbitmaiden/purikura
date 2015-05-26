#!/usr/bin/python

from PIL import Image
from pprint import pprint
import copy
import numpy
import sys
import math

Cb_Green = 92
Cr_Green = 86
Green = numpy.array([54,155,50])
Green = Green.astype("float")
# sys.exit()


tola = 50
tolb = 55

# green = Image.open("green.png")
# A = numpy.array(green)
# pprint(A)
# ycbcr = green.convert("YCbCr")
# A = numpy.ndarray((green.size[1], green.size[0], 3), 'u1', ycbcr.tostring())

# pprint(A)
# sys.exit()

# Greenish
# temp = 27

# definitely not green
# 961 + 2025
# temp 54

def colorclose(Cb_p, Cr_p, Cb_key, Cr_key, tola, tolb):
	temp = math.sqrt((Cb_key-Cb_p)**2+(Cr_key-Cr_p)**2)
	if temp < tola:
		return 0.0
	elif (temp < tolb):
		return (temp-tola)/(tolb-tola)
	else:
		return 1.0

def maskcolor(fg, bg, mask, green):
	return fg - (mask * green) + (bg * mask)

fg = Image.open("greenscreen.jpg")
fg_rgb = numpy.array(fg)

fg_ycbcr = fg.convert("YCbCr")
fg_array = numpy.ndarray((fg.size[1], fg.size[0], 3), 'u1', fg_ycbcr.tostring())

bg = Image.open("backgrounds/nebula.552.jpg")
bg_rgb = numpy.array(bg)

out = numpy.zeros((756,552,3))


for i in range(0, fg.size[1]):
	for j in range(0, fg.size[0]):
		thispixel = fg_array[i][j]
		mask = 1-colorclose(thispixel[1], thispixel[2], Cb_Green, Cr_Green, tola, tolb)
		for k in range(0,3):
			fgcolor = fg_rgb[i][j][k]
			bgcolor = bg_rgb[i][j][k]
			greencolor =  Green[k]
			out[i][j][k] = maskcolor(fgcolor, bgcolor, mask, greencolor)

final = Image.fromarray(out, "RGB")
final.save("final.jpg", "jpeg")


