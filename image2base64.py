import base64 
import os

source = './images/'
dest = './images/base64/'
files = [file for file in os.listdir(source) if file[-3:] in('png', 'ico', 'gif')]

for file in files:
    with open(source + file, 'rb') as f:
        img = base64.b64encode(f.read()) 
        with open(dest + file[:-4] + '.txt', 'wb') as g:
            g.write(img)

