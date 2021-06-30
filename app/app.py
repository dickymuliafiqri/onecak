from bs4 import BeautifulSoup as bs
from markupsafe import escape
from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
import requests
import re
import json
import os

app = Flask(__name__)
port = int(os.environ.get("PORT", 5000))

baseUrl = 'https://1cak.com/'
page = {
    "lol": "lol",
    "trend": "trending",
    "legend": "legendary",
    "shuffle": "shuffle"
}

def onecak(onecakPage):
    postList = []
    url = '{}{}'.format(baseUrl, onecakPage)
    page = requests.get(url)
    if not page.status_code == 200: raise Exception(page.status_code)
    content = page.content
    soup = bs(content, 'html.parser')
    for i in soup.findAll('div', id=re.compile(r'img_container')):
        postId = (i.a['href']).replace('/', '')
        postTitle = i.a.img['title']
        postUrl = baseUrl + postId
        postSrc = i.a.img['src']
        if re.search(r'unsave', postSrc): continue

        data = {
            "id": postId,
            "title": postTitle,
            "url": postUrl,
            "src": postSrc
        }
        postList.append(data)
    return postList

def onecakShuffle():
    postList = []
    post = ''
    url = '{}shuffle/'.format(baseUrl)
    while True:
        page = requests.get(url)
        if not page.status_code == 200: raise Exception(page.status_code)
        content = page.content
        soup = bs(content, 'html.parser')
        post = soup.find('div', id=re.compile(r'posts'))
        post = post.table.tr.td.img
        if not re.search(r'unsave', post['src']): break
    postId = page.url.replace('https://1cak.com/', '')
    postTitle = post['title']
    postUrl = page.url
    postSrc = post['src']
    data = {
        "id": postId,
        "title": postTitle,
        "url": postUrl,
        "src": postSrc
    }
    postList.append(data)
    return postList

@app.route('/', methods=['GET'])
def welcome():
    return jsonify({
        "name": "onecak",
        "credit": "https://1cak.com",
        "license": "MIT",
        "sourcecode": "https://github.com/dickymuliafiqri/onecak"
    })

@app.route('/<string:onecakPage>/', methods=['GET'])
def scrape(onecakPage):
    selPage = page[escape(onecakPage)]
    getOneCak = ''
    try:
        if selPage == 'shuffle':
            getOneCak = onecakShuffle()
        else:
            getOneCak = onecak(selPage)
        return jsonify({
            "length": len(getOneCak),
            "posts": getOneCak
        })
    except Exception as err:
        return jsonify({
            "error": err
        })


@app.errorhandler(HTTPException)
def exception_handler(e):
    res = e.get_response()
    res.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description
    })
    res.content_type = "application/json"
    return res

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=port)