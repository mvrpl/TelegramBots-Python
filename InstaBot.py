# -*- coding: utf-8 -*-
import os
import pickle
import random
import urllib2
from urlparse import urlparse
from os.path import splitext, basename
import requests
import tokens
import json
from time import sleep

if os.path.isfile('last_update_insta.txt') == True:
    file = open('last_update_insta.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % tokens.telegram_bot_instagram

while True:
    try:
        get_updates = json.loads(requests.get(url + 'getUpdates?offset='+str(last_update)).content)
    except:
        continue
    for update in get_updates['result']:
        if last_update < update['update_id']:
            last_update = update['update_id']
            file = open('last_update_insta.txt', 'w')
            pickle.dump(last_update, file)
            file.close()
            if 'location' in update['message']:
                location_photos = json.loads(requests.get('https://api.instagram.com/v1/media/search?lat='+str(update['message']['location']['latitude'])+'&lng='+str(update['message']['location']['longitude'])+'&access_token='+tokens.access_token).content)
                try:
                    rand_id = random.randint(0, len(location_photos['data'])-1)
                    photo = location_photos['data'][rand_id]['images']['standard_resolution']['url']
                    disassembled = urlparse(photo)
                    filename, file_ext = splitext(basename(disassembled.path))
                    photo_raw = open(filename+file_ext, 'wb')
                    photo_raw.write(urllib2.urlopen(photo).read())
                    img = open(filename+file_ext, 'rb')
                    requests.post(url + 'sendPhoto', files={'photo': img}, data={'chat_id': update['message']['chat']['id'], 'caption': location_photos['data'][rand_id]['link']})
                    os.unlink(filename+file_ext)
                except:
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Nothing found\nNada Encontrado' ))
            try:
                print(update['message']['text'])
            except:
                pass
            try:
                if u'/start' in update['message']['text']:
                    help_bot_en = u'Hi\nAvailable commands:\n/hashtag dogs to sending random photo with hashtag.\n\nLocation: Send your location to get a photo near you.\n\n'
                    help_bot = u'Olá\nComandos disponíveis:\n/hashtag riodejaneiro para enviar uma foto aleatória com a hashtag.\n\nLocalização: Envie sua localização para receber uma foto perto de você.'
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=help_bot_en+help_bot ))
                if u'/hashtag' in update['message']['text']:
                    try:
                        keyword = update['message']['text'].split(' ', 1)
                        tags_json = json.loads(requests.get('https://api.instagram.com/v1/tags/'+keyword[1]+'/media/recent?client_id='+tokens.client_id).content)
                        rand_id = random.randint(0, len(tags_json['data'])-1)
                        photo = tags_json['data'][rand_id]['images']['standard_resolution']['url']
                        disassembled = urlparse(photo)
                        filename, file_ext = splitext(basename(disassembled.path))
                        photo_raw = open(filename+file_ext, 'wb')
                        photo_raw.write(urllib2.urlopen(photo).read())
                        img = open(filename+file_ext, 'rb')
                        requests.post(url + 'sendPhoto', files={'photo': img}, data={'chat_id': update['message']['chat']['id'], 'caption': tags_json['data'][rand_id]['link']})
                        os.unlink(filename+file_ext)
                    except:
                        help_hashtag = open('help_hashtag.png', 'rb')
                        requests.post(url + 'sendPhoto', files={'photo': help_hashtag}, data={'chat_id': update['message']['chat']['id'], 'caption': u'Help use /hashtag command.\nComo usar comando /hashtag.'})
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=u'Example: /hashtag moon\nExemplo: /hashtag lua' ))
            except KeyError as e:
                print(e)
                continue
    sleep(3)
