from PIL import Image
import os
import shutil
import subprocess
import time

dpi = (300, 300)
photoCoords = ((38, 93), (590, 93), (38, 829), (590, 829))

def composite(path):
	final = Image.open('/home/pi/purikura/print/images/template.jpg')

	# just assume we have all four images by now
	os.chdir(path);
	for i in range(1,5): 

		photoName = 'photo' + str(i) + '.jpg'
		photo = Image.open(photoName)

		# check for overlay, we might not have one
		overlayName = 'overlay' + str(i) + '.png'
		if os.path.isfile(overlayName):
			overlay = Image.open(overlayName)
			photo.paste(overlay, (0,0), overlay)


		# now paste this file into the template
		x = i-1
		final.paste(photo, photoCoords[x])

	final.save('composite.jpg', "jpeg", dpi=dpi, quality=95)
	print "Print - Composite made for "+path
	return 1

def moveandprint(path):

	# move directory
	dirname = path.rpartition('/')[2]
	newpath = '/home/pi/purikura/print/printed/' + dirname
	shutil.move(path, newpath)
	print "Print - Moved " + dirname + " to printed dir"

	composite = newpath + '/composite.jpg'

	# send composite to print queue
	subprocess.call(["lp", composite])
	print "Print - Printed "+composite

	return 1

def process (path):
	success = composite(path)
	if success:
		moveandprint(path)


while True:
  # Scan for new directories in queue

  queue = '/home/pi/purikura/print/queue/'
  files = sorted(os.listdir(queue))
  for dirname in files:
    if (dirname == '.' or dirname == '..'):
      continue;
    print "Cron - Found "+dirname+", going to process"
    dirpath = queue + dirname
    process (dirpath)

    # breaking here to let the next iteration handle any remaining files
    break

  print "sleeping for 10 seconds"
  time.sleep(10)

















