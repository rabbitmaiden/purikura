import chromakey
from PIL import Image
import time

start = time.time()
fg = Image.open("../photo/greenscreen.jpg")
bg = Image.open("../photo/backgrounds/nebula.552.jpg")

now = time.time()
print "Loading photos took %f seconds" % (now - start)
start = now

out = chromakey.chromakey(fg, bg)

now = time.time()
print "Chromakey took %f seconds" % (now - start)
start = now

final = Image.fromarray(out, "RGB")
final.save("final.jpg", "jpeg", quality=90)

now = time.time()
print "Saving took %f seconds" % (now - start)