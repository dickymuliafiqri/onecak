from bs4 import BeautifulSoup as bs
from time import sleep
import crud
import requests
import re

baseUrl = 'https://1cak.com/'
database = crud.OnecakDB()
database.run_command(crud.posts_table)
database.run_command(crud.tasks_table)

session = {
    "sess_str": "25014de81886067dd4a7ebcfa6de9c8d",
    "sess_user_id": "1596365"
}

def getRecent():
    url = 'https://1cak.com/lol/'
    page = requests.get(url, cookies=session)
    if not page.status_code == 200: raise Exception(page.status_code)
    content = page.content
    soup = bs(content, 'html.parser')
    recent = soup.find('a', target="_blank")
    postId = (recent['href']).replace('/', '')
    return int(postId)

def onecak(postId):
    posts = None
    post = None
    nsfw = False
    gif = False

    page = requests.get('{}{}'.format(baseUrl, postId), cookies=session)
    if not page.status_code == 200: raise Exception(page.status_code)
    content = page.content
    soup = bs(content, 'html.parser')
    try:
        posts = soup.find('div', id=re.compile(r'posts'))
        posts = posts.table.tr.td
        post = posts.img
        try:
            post['title']
        except KeyError:
            post = None

        if not post:
            post = posts.iframe
            gif = True
        nsfw = soup.find('img', src=re.compile(r'nsfw'))
        nsfw = True if nsfw else False
    except AttributeError:
        err = soup.find('img', src=re.compile(r'error'))
        if err: raise Exception(404)

    postUrl = page.url
    postSrc = post['src']
    postTitle = ''
    if gif:
        gifTitle = posts.div.h3
        postTitle = gifTitle.string
    else:
        postTitle = post['title']

    database.run_command(crud.post_insert, (postId, postTitle, postUrl, postSrc, gif, nsfw))

def main():
    recent = None
    x = 0

    if database.run_command(crud.tasks_length) == 0:
        database.run_command(crud.task_insert, (0, 0, 0))
    last_scan = database.run_command('SELECT last_scan FROM tasks')
    if last_scan is not None:
        i = database.run_command('SELECT last_scan FROM tasks')

    i = 1 if i == 0 else i
    try:
        recent = getRecent()
    except Exception as err:
        print('Failed get recent post on 1cak: ', err)

    while True:
        if recent == i: break
        try:
            onecak(i)
            print('Success: {}{}'.format(baseUrl, i))
        except Exception as err:
            print('Failed: {}{} - {}'.format(baseUrl, i, err))
        finally:
            posts = database.run_command(crud.posts_length)
            database.run_command(crud.tasks_update, (recent, i, posts, 1))

        i+=1
        x+=1
        sleep(1)
        if x >= 500: break

    print('\n\n#####')
    print('Recent post: {}'.format(recent))
    print('Total post: {}'.format(posts))
    print('Process ended')

if __name__ == '__main__':
    main()
