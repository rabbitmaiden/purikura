from PIL import Image
dpi = (300, 300)
photoCoords = ((38, 93), (590, 93), (38, 829), (590, 829))

final = Image.open('template.jpg')

for x in range(0,4):
  filename = 'comp' + str(x) + '.jpg'
  print "adding "+filename
  photo = Image.open(filename)
  final.paste(photo, photoCoords[x])

final.save("./composite.jpg", "jpeg", dpi=dpi,quality=95)
