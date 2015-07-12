# -*- coding: utf-8 -*-
from os.path import basename, splitext
import urllib2
from urlparse import urlparse
import tokens
import pickle
import json
import requests
import os
from time import sleep

if os.path.isfile('last_update_wall.txt') == True:
    file = open('last_update_wall.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % tokens.telegram_bot_wallpapers

while True:
    try:
        get_updates = json.loads(requests.get(url + 'getUpdates').content)
    except:
        continue
    for update in get_updates['result']:
        if last_update < update['update_id']:
            last_update = update['update_id']
            file = open('last_update_wall.txt', 'w')
            pickle.dump(last_update, file)
            file.close()
            print(update['message']['text'])
            try:
                if u'/start' in update['message']['text']:
                    help_bot = u'Olá\nComandos disponíveis:\n/randomwall: Send random wallpaper image.'
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=help_bot ))
                if u'/randomwall' in update['message']['text']:
                    photo_WS = json.loads(requests.get('https://api.desktoppr.co/1/wallpapers/random').content)
                    photo_url = photo_WS['response']['image']['thumb']['url']
                    disassembled = urlparse(photo_url)
                    filename, file_ext = splitext(basename(disassembled.path))
                    photo_raw = open(filename+file_ext, 'wb')
                    photo_raw.write(urllib2.urlopen(photo_url).read())
                    img = open(filename+file_ext, 'rb')
                    message_return = 'Resolution: %sX%s\nFull: %s' % (photo_WS['response']['width'], photo_WS['response']['height'], photo_WS['response']['image']['url'])
                    requests.post(url + 'sendPhoto', files={'photo': img}, data={'chat_id': update['message']['chat']['id'], 'caption': message_return})
                    os.unlink(filename+file_ext)
            except KeyError as e:
                print(e)
                continue
    sleep(3)
