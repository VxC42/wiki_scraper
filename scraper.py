from flask import Flask, render_template, request, send_from_directory
from flask_restful import Api, Resource
from bs4 import BeautifulSoup
import requests
import json
import base64

app = Flask(__name__)
api = Api(app)

FILE = "/game.json"

class send_json(Resource):
    def get(self):
        f = open('game.json',)
        data = json.load(f)
        return (data)

api.add_resource(send_json, "/send")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST', 'GET'])
def submit_game():
    if request.method == "POST":
        error = ""
        game_wiki_text = ""
        game_title = request.form['game_input']

        # If the user's input is empty
        if game_title == "":
            return render_template('index.html', error="Please enter a game title.")

        url = "https://en.wikipedia.org/wiki/" + game_title
        page = requests.get(url)

        # If the wiki page does not exist
        if str(page) == "<Response [404]>":
            return render_template('index.html', error="Sorry there is not information on this title: Wiki not found.")


        # Determine if title is a video game
        cattags = page.text.split('id="mw-normal-catlinks')
        tagsoup = BeautifulSoup(cattags[1], 'html.parser')
        tagresults = tagsoup.findAll('li')
        tagwords = ""
        for tag in tagresults:
            tagwords += tag.text.strip()

        if "video game" not in tagwords:
            if "Disambiguation pages" in tagwords:
                print('HI')
                test = []
                cut_footer = page.text.split('id="disambigbox"')
                cut_header = cut_footer[0].split('class="mw-headline"', 1)
                soup = BeautifulSoup(cut_header[1], 'html.parser')
                results = soup.findAll('li')
                for result in results:
                    test.append(str(result))
                print(test)
                return render_template('index.html', multiples=test)
            try:
                #check if disambiguous page exists
                disam_title = game_title + "_(disambiguation)"
                url = "https://en.wikipedia.org/wiki/" + disam_title
                page = requests.get(url)
                test = []
                cut_footer = page.text.split('id="disambigbox"')
                cut_header = cut_footer[0].split('<span class="toctext">See also</span>')
                soup = BeautifulSoup(cut_header[1], 'html.parser')
                results = soup.findAll('li')
                for result in results:
                    test.append(str(result))
                return render_template('index.html', multiples=test)
            except:
                return render_template('index.html', error="Sorry there is no information on this title: Wiki found, but does not appear to be a video game")

        cut_footer = page.text.split('id="Notes"')
        cut_header = cut_footer[0].split('id="siteSub"')

        soup = BeautifulSoup(cut_header[1], 'html.parser')
        results = soup.findAll('p')
        for result in results:
            game_wiki_text += result.text.strip()

        #Output JSON file
        output = {game_title: game_wiki_text}
        with open('game.json', 'w') as json_file:
            json.dump(output, json_file)

        return render_template('index.html', success="Success, please wait")

    else:
        return render_template('index.html')

@app.route('/wiki/<string:selection>')
def picked_game(selection):
    game_wiki_text = ""
    url = "https://en.wikipedia.org/wiki/" + selection
    page = requests.get(url)
    cut_footer = page.text.split('id="Notes"')
    cut_header = cut_footer[0].split('id="siteSub"')
    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('p')
    # If the wiki page does not exist
    if str(page) == "<Response [404]>":
        return render_template('index.html', error="Sorry there is not information on this title: Wiki not found.")

    # Determine if title is a video game
    cattags = page.text.split('id="mw-normal-catlinks')
    tagsoup = BeautifulSoup(cattags[1], 'html.parser')
    tagresults = tagsoup.findAll('li')
    tagwords = ""
    for tag in tagresults:
        tagwords += tag.text.strip()

    if "video game" not in tagwords:
        if "Disambiguation pages" in tagwords:
            test = []
            cut_footer = page.text.split('id="disambigbox"')
            cut_header = cut_footer[0].split('<span class="toctext">See also</span>')
            soup = BeautifulSoup(cut_header[1], 'html.parser')
            results = soup.findAll('li')
            for result in results:
                test.append(str(result))
            print(test)
            return render_template('index.html', multiples=test)
        try:
            # check if disambiguous page exists
            disam_title = selection + "_(disambiguation)"
            url = "https://en.wikipedia.org/wiki/" + disam_title
            page = requests.get(url)
            test = []
            cut_footer = page.text.split('id="disambigbox"')
            cut_header = cut_footer[0].split('<span class="toctext">See also</span>')
            soup = BeautifulSoup(cut_header[1], 'html.parser')
            results = soup.findAll('li')
            for result in results:
                test.append(str(result))
            return render_template('index.html', multiples=test)
        except:
            return render_template('index.html',
                                   error="Sorry there is no information on this title: Wiki found, but does not appear to be a video game")

    cut_footer = page.text.split('id="Notes"')
    cut_header = cut_footer[0].split('id="siteSub"')

    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('p')
    for result in results:
        game_wiki_text += result.text.strip()

    # Output JSON file
    output = {selection: game_wiki_text}
    with open('game.json', 'w') as json_file:
        json.dump(output, json_file)

    return render_template('index.html', success="Success, please wait")

@app.route('/results')
def display_results():
    with open('exampleCollageSend.json') as f:
        data = json.load(f)

    x = data['ImageData']
    title = data['Title']
    filename = 'static/images/'+title+'.png'
    y = bytes(x.split(",")[1], 'utf-8')
    image_64_decode = base64.decodebytes(y)
    image_result = open(filename, 'wb')  # create a writable image and write the decoding result
    image_result.write(image_64_decode)

    return render_template('results.html', images = [[title, filename]])



if __name__ == "__main__":
    app.run(debug=True)
