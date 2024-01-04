

########## IMPORTS ##########

from browser import document, alert as _alert, ajax, window
from browser.local_storage import storage
from html import escape
import json

def alert(*args, sep=' ', end=''):
    _alert(sep.join([str(x) for x in args]) + end)

import sys

class stderr_writer:
    def write(self, x):
        document.write(escape(x).replace('\n', '<br>').replace(' ', '&nbsp;'))

sys.stderr = stderr_writer()


########## CONSTANTS ##########


saddr = '127.0.0.1'


########## FUNCTIONS ##########


def set_post(i):
    def read(req):
        if req.status == 200:
            r = json.loads(req.text)
            title = r['t']
            name = r['n']
            text = r['x']
            document['v-title'].textContent = title
            document['v-name'].textContent = name
            document['v-text'].textContent = text
    ajax.get(f'https://{saddr}/getpost?{i}', oncomplete=read)

def send_post(title, text):
    if 'posts-left' in storage:
        if int(storage['posts-left']) < 1:
            alert('You can\'t post again today. You can post 32 posts every day.')
            return
    goback = True
    def read(req):
        nonlocal goback
        if req.status == 400:
            alert(req.statusText.capitalize())
            goback = False
        elif req.status == 403:
            window.location.replace("https://blocked.goguardian.com/blocked.html")
        elif req.status == 451:
            alert('Stop trying to hack the system. YOU CAN\'T POST TOMMOROW HAHAHAHA!!!!!')
        elif req.status == 418:
            alert('Profanity detected, post not added.')
            goback = False
        else:
            print(req.responseText)
            t = json.loads(req.responseText)
            storage['posts-left'] = str(t['p'])
            storage['imgs-left'] = str(t['g'])
            storage['megs-left'] = str(t['m'])
            print('test')
            alert('Post added. Link: https://uwatch2.github.io/?m=v&p=' + str(t['i']))
    ajax.post(f'https://{saddr}/addpost', data=json.dumps({'title':title, 'text':text}), oncomplete=read)

def set_trending():
    def read(req):
        if req.status != 200:
            alert(f'Error while fetching trending')
            return
        out = req.read()
        if out == None:
            return
        a = 0
        for _post in out.split('\r\n'):
            if _post.strip() == '':
                continue
            a += 1
            post = json.loads(_post)
            title = post['t']
            name = post['n']
            text = post['x']
            full = f'''<div id="view{a}" class="view"><table id="v{a}-header" class="v-header"><tr><td id="v{a}-title" class="v-title">{escape(title)}</td><td id="v{a}-name" class="v-name">{escape(name)}</td></tr></table><div id="v{a}-text" class="v-text">{escape(text)}</div></div>'''
            document['trending'].innerHTML += full.replace('\n', '<br>')
            document['trending'].innerHTML += '<br><br><br>'
    ajax.get(f'https://{saddr}/gettrending', oncomplete=read)

def goto_trending(_ev=None):
    document['trending'].style.display = 'block'
    document['create'].style.display = 'none'
    document['view'].style.display = 'none'
    document['searchr'].style.display = 'none'
    set_trending()

def goto_create(_ev=None):
    document['trending'].style.display = 'none'
    document['create'].style.display = 'block'
    document['view'].style.display = 'none'
    document['searchr'].style.display = 'none'

def add_post_btn(_ev=None):
    repeat = send_post(document['c-title'].value, document['c-text'].value)
    if not repeat:
        document['trending'].style.display = 'block'
        document['create'].style.display = 'none'
        document['view'].style.display = 'none'
        document['searchr'].style.display = 'none'


########## MAIN ##########


if document.query.getvalue('m', '') == 'v':
    document['trending'].style.display = 'none'
    document['create'].style.display = 'none'
    document['view'].style.display = 'block'
    document['searchr'].style.display = 'none'
    i = int(document.query.getvalue('p', '-1'))
    set_post(i)
else:
    document['trending'].style.display = 'block'
    document['create'].style.display = 'none'
    document['view'].style.display = 'none'
    document['searchr'].style.display = 'none'
    document['tab-trending'].bind('click', goto_trending)
    document['tab-create'].bind('click', goto_create)
    document['c-add'].bind('click', add_post_btn)
    set_trending()
