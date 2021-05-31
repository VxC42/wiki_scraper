"""
Title: Wiki Scrape for Game Matcher
Author: Valerie Chin chinv@oregonstate.edu
Date: 5/30/2021
Description: Wiki Scraper that specifically scrape text from
             video game wikis. Displays information from
             a previous services that creates a word/image collage
             from the results of this wiki scrape.
"""

from flask import Flask, render_template, request, redirect
from flask_restful import Api, Resource
from bs4 import BeautifulSoup
import requests
import json
import base64
import time

app = Flask(__name__)
api = Api(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SERVER_NAME'] = 'valchin.com'

class send_json(Resource):
    """
    Sends the game.json file to the service
    that requests it from valchin.com/sendjson2021
    """
    def get(self):
        f = open('game.json',)
        data = json.load(f)
        return (data)

api.add_resource(send_json, "/sendjson2021")

def save_collages(data):
    """
    Function that is passed the data from the
    previous function, and saves the data (2 collages)
    into files that can be displayed for the user.
    """

    # raw data
    imgraw = data['collageData']
    wordraw = data['wordCloudData']

    # Decode collage's rawdata
    imgCollage = bytes(imgraw.split(",")[1], 'utf-8')
    wordCollage = bytes(wordraw.split(",")[1], 'utf-8')
    imgCollageDecode = base64.decodebytes(imgCollage)
    wordCollageDecode = base64.decodebytes(wordCollage)

    # Opens and saves the image files
    imgCollageResult = open('static/images/imageCollage.png', 'wb')
    wordCollageResult = open('static/images/wordCollage.png', 'wb')
    imgCollageResult.write(imgCollageDecode)
    wordCollageResult.write(wordCollageDecode)

def gettags(page):
    """
    Function grabs that tags located
    at the bottom of the given wikipedia page.
    Returns a list of tagwords.
    """
    cattags = page.text.split('id="mw-normal-catlinks')
    tagsoup = BeautifulSoup(cattags[1], 'html.parser')
    tagresults = tagsoup.findAll('li')
    tagwords = ""
    for tag in tagresults:
        tagwords += tag.text.strip()

    return tagwords

def getwikis(page):
    """
    Functions gets a list of links is the user's
    input leads the service to a 'disambiguous page'
    of wiki links.
    Returns a list of links to be displayed for the user
    """
    wikis = []
    formatted_wikis=[]

    # Checks if the wiki page has mw-headline,
    # which indicates there is a Table of Contents
    # that we don't want. Example: Overwatch
    if 'class="mw-headline"' in page.text:
        cut_footer = page.text.split('id="disambigbox"')
        cut_header = cut_footer[0].split('class="mw-headline"', 1)
    # Check if the wiki page does not have
    # a Table of Contents. Example: Knights of the Old Republic
    else:
        cut_footer = page.text.split('id="disambigbox"')
        cut_header = cut_footer[0].split('id="mw-content-text"')

    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('li')
    for result in results:
        wikis.append(str(result))
    for wiki in wikis:
        insert = wiki.find("href")
        newstr = wiki[:insert] + 'onClick="toggleImage()" ' + wiki[insert:]
        formatted_wikis.append(newstr)
    return formatted_wikis

def getDisambigPage(game_title):
    """
    Function for if Game Wiki page isn't found,
    it will try see check if there is a
    disambiguous page first before stopping the search
    Returns a page if one is found.
    """
    link = game_title + "_(disambiguation)"
    url = "https://en.wikipedia.org/wiki/" + link
    page = requests.get(url)
    return page

def getDisambigLinks(page):
    """
    Function if a Disambiguous page is found from getDisambigPage()
    then it will pull all the links from that disambiguous page and
    return a list of links. Example: Destiny
    """
    links = []
    cut_footer = page.text.split('id="disambigbox"')
    cut_header = cut_footer[0].split('<span class="toctext">See also</span>')
    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('li')
    for result in results:
        links.append(str(result))
    return links

def getWikiText(page, game_title):
    """
    Function that will scrape all the text on a given wiki page
    if that wiki page is a game's wiki page.
    Saves the wiki's text into a json file.
    """
    cut_footer = page.text.split('id="Notes"')
    cut_header = cut_footer[0].split('id="siteSub"')

    wikiText = ""
    soup = BeautifulSoup(cut_header[1], 'html.parser')
    results = soup.findAll('p')
    for result in results:
        wikiText += result.text.strip()

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

        if "/.." in game_title or "./" in game_title:
            return render_template('index.html', error="Value entered in invalid, please try again.")

        if game_title == "":
            return render_template('index.html', error="Please enter a game title.")

        if str(page) == "<Response [404]>":
            return render_template('index.html', error="Sorry there is no game Wiki for this title.")

        tags = gettags(page)

        # Processes what happens if the video game tag is not on the wiki page given.
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

    save_collages(data)
    ifilename = 'static/images/imageCollage.png'
    wfilename = 'static/images/wordCollage.png'

    return render_template('results.html', images = [ifilename, wfilename])

@app.route('/wiki/results/<string:game_title>')
def display_wikiresults(game_title):

    #Request data for image collage and word collage from previous service.
    response = requests.get("http://collage.jacobeckroth.com/apirequest/" + game_title)
    time.sleep(5)
    data = response.json()

    save_collages(data)
    ifilename = 'static/images/imageCollage.png'
    wfilename = 'static/images/wordCollage.png'

    return render_template('results.html', images = [ifilename, wfilename])

@app.route('/reset')
def reset_to_index():
    return redirect('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)

