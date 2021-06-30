from bs4 import BeautifulSoup as bs
from time import sleep
import requests
import re
import json

baseUrl = 'https://1cak.com/'
database = json.load(open('./api/onecak.json'))
postList = database['posts']

session = {
    "sess_str": "25014de81886067dd4a7ebcfa6de9c8d",
    "sess_user_id": "1596365"
}

def onecak(postId):
    post = ''
    nsfw = False

    page = requests.get('{}{}'.format(baseUrl, postId), cookies=session)
    if not page.status_code == 200: raise Exception(page.status_code)
    content = page.content
    soup = bs(content, 'html.parser')
    try:
        post = soup.find('div', id=re.compile(r'posts'))
        post = post.table.tr.td.img
        nsfw = soup.find('img', src=re.compile(r'nsfw'))
        nsfw = True if nsfw else False
    except AttributeError:
        err = soup.find('img', src=re.compile(r'error'))
        if err: raise Exception(404)

    postTitle = post['title']
    postUrl = page.url
    postSrc = post['src']
    data = {
        "id": postId,
        "title": postTitle,
        "url": postUrl,
        "src": postSrc,
        "nsfw": nsfw
    }
    postList.append(data)

if __name__ == '__main__':
    x = 0
    i = database['lastscan']
    recent = requests.get('https://onecak.herokuapp.com/lol/')
    recent = recent.json()
    recent = int(recent['posts'][0]['id'])
    database['lastpost'] = recent

    while True:
        if recent == i: break
        indexed = 0
        try:
            for indx in range(500):
                try:
                    if database['posts'][len(postList)-indx]['id'] == i: 
                        indexed = 1
                        break
                except IndexError:
                    pass
            if indexed: raise Exception('Already indexed')
            onecak(i)
            print('Success: {}{}'.format(baseUrl, i))
        except Exception as err:
            print('Failed: {}{} - {}'.format(baseUrl, i, err))
            pass

        i+=1
        x+=1
        database['length'] = len(postList)
        database['lastscan'] = i
        with open('./api/onecak.json', 'w') as outfile:
            outfile.write(json.dumps(database, indent=4))
        if x >= 5000: break
        sleep(1)
    print('\n\n#####')
    print('Recent post: {}'.format(recent))
    print('Total post: {}'.format(len(postList)))
    print('Process ended')