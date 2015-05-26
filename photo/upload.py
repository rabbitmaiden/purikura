import requests
import pprint


url = 'http://192.168.1.120/'
files = [('photo1', open('../test/photo1.jpg', 'rb')), ('photo2', open('../test/photo2.jpg', 'rb')), ('photo3', open('../test/photo3.jpg', 'rb')), ('photo4', open('../test/photo4.jpg', 'rb'))]
params = {'action': 'photo'}
r = requests.post(url, files=files, params=params)
pprint.pprint(r.text)
