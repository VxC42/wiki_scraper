import requests
import base64

BASE = "http://valchin.com/"
gametitle="Minecraft"

response = requests.get("http://collage.jacobeckroth.com/apirequest/Minecraft")
data = response.json()
if data["title"] == gametitle:
    print("True")
else:
    print("False")


"""

import base64
import json
import requests
import io
import json
import base64
import logging

from flask import Flask, request, jsonify, abort
app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
api = 'https://thebacklog340.herokuapp.com/wordcloud66'
image_file = 'wordCloud.png'
with open(image_file, "rb") as f:
    im_bytes = f.read()
im_b64 = base64.b64encode(im_bytes).decode("utf8")
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
payload = json.dumps({"image": im_b64, "other_key": "value"})
response = requests.post(api, data=payload, headers=headers)
try:
    data = response.json()
    print(data)
except requests.exceptions.RequestException:
    print(response.text)"""