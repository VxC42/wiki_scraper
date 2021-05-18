import base64
import json

with open('exampleCollageSend.json') as f:
    data = json.load(f)

x = data['ImageData']
y = bytes(x.split(",")[1], 'utf-8')
image_64_decode = base64.decodebytes(y)
image_result = open('display.png', 'wb') # create a writable image and write the decoding result
image_result.write(image_64_decode)

