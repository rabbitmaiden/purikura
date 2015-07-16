import chromakey
from PIL import Image

fg = Image.open("greenscreen.jpg")
bg = Image.open("backgrounds/nebula.552.jpg")

final = chromakey.chromakey(fg, bg)
final.save("final.jpg", "jpeg", quality=90)


# # "Decode" the image from the array, preserving colour
# image = cv2.imread("chromakey.jpg")

# pMOG = cv2.BackgroundSubtractorMOG()

# fgmask = pMOG.apply(image)
# cv2.imwrite("pmog.jpg", fgmask)