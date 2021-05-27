from flask import Flask, render_template, request, redirect
from flask_restful import Api, Resource
from bs4 import BeautifulSoup
import requests
import json
import base64
import time

app = Flask(__name__)
api = Api(app)
#app.config['SERVER_NAME'] = 'valchin.com'

class send_json(Resource):
    def get(self):
        f = open('game.json',)
        data = json.load(f)
        return (data)

api.add_resource(send_json, "/sendjson2021")

def save_collages(data):
    # Collage's raw data
    imgraw = data['collageData']
    wordraw = data['wordCloudData']

    # Decode collage's rawdata
    imgCollage = bytes(imgraw.split(",")[1], 'utf-8')
    wordCollage = bytes(wordraw.split(",")[1], 'utf-8')
    imgCollageDecode = base64.decodebytes(imgCollage)
    wordCollageDecode = base64.decodebytes(wordCollage)

    imgCollageResult = open('static/images/imageCollage.png', 'wb')
    wordCollageResult = open('static/images/wordCollage.png', 'wb')

    imgCollageResult.write(imgCollageDecode)
    wordCollageResult.write(wordCollageDecode)

def gettags(page):
    # Determine if title is a video game
    cattags = page.text.split('id="mw-normal-catlinks')
    tagsoup = BeautifulSoup(cattags[1], 'html.parser')
    tagresults = tagsoup.findAll('li')
    tagwords = ""
    for tag in tagresults:
        tagwords += tag.text.strip()

    return tagwords

def getwikis(page):
    wikis = []
    cut_footer = page.text.split('id="disambigbox"')
    cut_header = cut_footer[0].split('class="mw-headline"', 1)
    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('li')
    for result in results:
        wikis.append(str(result))
    return wikis

def getDisambigPage(game_title):
    link = game_title + "_(disambiguation)"
    url = "https://en.wikipedia.org/wiki/" + link
    page = requests.get(url)
    return page

def getDisambigLinks(page):
    links = []
    cut_footer = page.text.split('id="disambigbox"')
    cut_header = cut_footer[0].split('<span class="toctext">See also</span>')
    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('li')
    for result in results:
        links.append(str(result))
    return links

def getWikiText(page, game_title):
    cut_footer = page.text.split('id="Notes"')
    cut_header = cut_footer[0].split('id="siteSub"')

    wikiText = ""
    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('p')
    for result in results:
        wikiText += result.text.strip()

    # Output JSON file
    output = {game_title: wikiText}
    with open('game.json', 'w') as json_file:
        json.dump(output, json_file)
    return wikiText

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/', methods=['POST', 'GET'])
def submit_game():
    if request.method == "POST":
        game_title = request.form['game_input']
        url = "https://en.wikipedia.org/wiki/" + game_title
        page = requests.get(url)

        # If the user's input is empty
        if game_title == "":
            return render_template('index.html', error="Please enter a game title.")

        # If the wiki page does not exist
        if str(page) == "<Response [404]>":
            return render_template('index.html', error="Sorry there is no game Wiki for this title.")

        tags = gettags(page)

        if "video game" not in tags:
            if "Disambiguation pages" in tags:
                wiki_pages = getwikis(page)
                return render_template('index.html', multiples=wiki_pages)
            try:
                page = getDisambigPage(game_title)
                disam_links = getDisambigLinks(page)
                return render_template('index.html', multiples=disam_links)
            except:
                return render_template('index.html', error="Wiki found, but does not appear to be a video game")

        getWikiText(page, game_title)

        return redirect('results/'+game_title)

    else:
        return render_template('index.html')

@app.route('/wiki/<string:game_title>')
def picked_game(game_title):
    url = "https://en.wikipedia.org/wiki/" + game_title
    page = requests.get(url)

    # If the wiki page does not exist
    if str(page) == "<Response [404]>":
        return render_template('index.html', error="Sorry there is no game Wiki for this title.")

    tags = gettags(page)

    if "video game" not in tags:
        if "Disambiguation pages" in tags:
            wiki_pages = getwikis(page)
            return render_template('index.html', multiples=wiki_pages)
        try:
            page = getDisambigPage(game_title)
            disam_links = getDisambigLinks(page)
            return render_template('index.html', multiples=disam_links)
        except:
            return render_template('index.html',
                                   error="Wiki found, but does not appear to be a video game")

    getWikiText(page, game_title)

    return redirect('results/'+game_title)


@app.route('/results/<string:game_title>')
def display_res(game_title):
    # Request data for image collage and word collage from previous service.
    response = requests.get("http://collage.jacobeckroth.com/apirequest/" + game_title)
    data = response.json()

    #Ensure data received matches the game title that the user inputted
    if data["title"] == game_title:
        save_collages(data)
        ifilename = 'static/images/imageCollage.png'
        wfilename = 'static/images/wordCollage.png'
    else:
        return("help")

    return render_template('results.html', images = [ifilename, wfilename])

@app.route('/wiki/results/<string:game_title>')
def display_wikiresults(game_title):

    #Request data for image collage and word collage from previous service.
    response = requests.get("http://collage.jacobeckroth.com/apirequest/" + game_title)
    time.sleep(5)
    data = response.json()

    #Ensure data received matches the game title that the user inputted
    if data["title"] == game_title:
        save_collages(data)
        ifilename = 'static/images/imageCollage.png'
        wfilename = 'static/images/wordCollage.png'
    else:
        return("help")

    return render_template('results.html', images = [ifilename, wfilename])

@app.route('/reset')
def reset_to_index():
    return redirect('index.html')


if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=80, debug=True)
    app.run(host='127.0.0.1', port=5000, debug=True)
