from bs4 import BeautifulSoup as bs
from markupsafe import escape
from flask import Flask, jsonify
import requests
import re
import json

app = Flask(__name__)

baseUrl = 'https://1cak.com'
page = {
    "lol": "lol",
    "trend": "trend",
    "legend": "legendary",
    "shuffle": "shuffle"
}

def onecak(onecakPage):
    listPost = []
    url = '{}/{}'.format(baseUrl, onecakPage)
    page = requests.get(url)
    print(page.status_code)
    if not page.status_code == 200: raise Exception(page.status_code)
    content = page.content
    soup = bs(content, 'html.parser')
    for i in soup.findAll('div', id=re.compile(r'img_container')):
        postId = i.a['href']
        postTitle = i.a.img['title']
        postUrl = baseUrl + postId
        postSrc = i.a.img['src']
        if re.search(r'unsave', postSrc): continue
        try:
            for x in len(listPost):
                if listPost[x].id == postId: continue
        except (AttributeError, TypeError):
            pass

        data = {
            "id": postId,
            "title": postTitle,
            "url": postUrl,
            "src": postSrc
        }
        listPost.append(data)
    return listPost

@app.route('/', methods=['GET'])
def welcome():
    return jsonify({
        "name": "onecak",
        "credit": "https://1cak.com",
        "license": "MIT",
        "sourcecode": "https://github.com/dickymuliafiqri/onecak"
    })

@app.route('/<onecakPage>/', methods=['GET'])
def scrape(onecakPage):
    selPage = page[escape(onecakPage)]
    try:
        getOneCak = onecak(selPage)
        return jsonify({
            "url": "{}/{}".format(baseUrl, selPage),
            "posts": getOneCak,
            "length": len(getOneCak)
        })
        # onecak(selPage)
    except Exception as err:
        return jsonify({
            "Error": err
        })

@app.errorhandler(400)
def notFound(e):
    return jsonify({
        "Error": "400 Bad Request"
    })

@app.errorhandler(404)
def notFound(e):
    return jsonify({
        "Error": "404 Not Found"
    })

@app.errorhandler(405)
def notFound(e):
    return jsonify({
        "Error": "405 Method Not Allowed"
    })

@app.errorhandler(408)
def notFound(e):
    return jsonify({
        "Error": "408 Request Timeout"
    })

@app.errorhandler(500)
def notFound(e):
    return jsonify({
        "Error": "500 Internal Server Error"
    })

@app.errorhandler(502)
def notFound(e):
    return jsonify({
        "Error": "502 Bad Gateway"
    })

@app.errorhandler(503)
def notFound(e):
    return jsonify({
        "Error": "503 Service Unavailable"
    })

@app.errorhandler(504)
def notFound(e):
    return jsonify({
        "Error": "504 Gateway Timeout"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000)