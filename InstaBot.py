# -*- coding: utf-8 -*-
import locale
import os
import pickle
import random
import re
import urllib2
from urlparse import urlparse
from os.path import splitext, basename
import requests
import tokens
import json
from time import sleep
from mechanize import Browser
from bs4 import BeautifulSoup
import sys

reload(sys)
sys.setdefaultencoding('UTF8')

locale.setlocale(locale.LC_ALL, 'pt_BR.utf-8')

def find_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""

def Top10Followers():
    ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
    br = Browser()
    br.set_handle_robots(False)
    br.addheaders = [('User-Agent', ua), ('Accept', '*/*')]
    br.open('http://socialblade.com/instagram/top/10/followers')
    soup = BeautifulSoup(br.response().read())
    table = soup.find('div', {'class':'content-module-wide'}).contents
    top10 = []
    for i in xrange(1, 120, 2):
        top10.append(table[i].text.replace(',', '.'))
    top10return = []
    for n in range(0, 10):
        top10return.append('%s | %s | %s | %s | %s\n' % ([top10[x:x+6] for x in xrange(0, len(top10), 6)][n][0], [top10[x:x+6] for x in xrange(0, len(top10), 6)][n][2], [top10[x:x+6] for x in xrange(0, len(top10), 6)][n][3], [top10[x:x+6] for x in xrange(0, len(top10), 6)][n][4], [top10[x:x+6] for x in xrange(0, len(top10), 6)][n][5]))
    return ''.join(top10return)

def AccountInfo(username):
    br = Browser()
    br.set_handle_robots(False)
    br.open('https://instagram.com/'+username)
    soup = BeautifulSoup(br.response().read())
    script_tag = soup.find('script', text=re.compile('window\._sharedData'))
    shared_data = script_tag.string.partition('=')[-1].strip(' ;')
    user = json.loads(shared_data)
    follows = user['entry_data']['ProfilePage'][0]['user']['follows']['count']
    followed_by = user['entry_data']['ProfilePage'][0]['user']['followed_by']['count']
    media_count = user['entry_data']['ProfilePage'][0]['user']['media']['count']
    bio = user['entry_data']['ProfilePage'][0]['user']['biography']
    is_private = user['entry_data']['ProfilePage'][0]['user']['is_private']
    private = 'Yes/Sim' if is_private == True else u'No/Não'
    is_verified = user['entry_data']['ProfilePage'][0]['user']['is_verified']
    verified = 'Yes/Sim' if is_verified == True else u'No/Não'
    user_id = user['entry_data']['ProfilePage'][0]['user']['id']
    return u'Following/Seguindo: %s\nFollowers/Seguidores: %s\nMedia Count/Número de fotos/vídeos: %s\nBio: %s\nPrivate Profile/Perfil Privado: %s\nVerified Profile/Perfil Verificado: %s\nUser ID/ID do usuário: %s' % (locale.format('%d', int(follows), 1), locale.format('%d', int(followed_by), 1), media_count, bio, private, verified, user_id)

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
                print(update['message']['from']['first_name'], update['message']['text'])
            except:
                pass
            try:
                if u'/start' in update['message']['text']:
                    help_bot_en = u'Hi\nAvailable commands:\n/top10followers: Get top 10 users most followers.\n/hashtag dogs to sending random photo with hashtag.\n/info marcos_dev: Send account info.\nLocation: Send your location to get a photo near you.\n\n'
                    help_bot = u'Olá\nComandos disponíveis:\n/top10followers: Obtem as 10 contas com mais seguidores.\n/hashtag riodejaneiro para enviar uma foto aleatória com a hashtag.\n/info marcos_dev: Envia infos do usuário.\nLocalização: Envie sua localização para receber uma foto perto de você.'
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=help_bot_en+help_bot ))
                if u'/info' in update['message']['text']:
                    keyword = update['message']['text'].split(' ', 1)
                    try:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=AccountInfo(keyword[1]) ))
                    except:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=u'User does not exist/Usuário não existe' ))
                if u'/top10followers' in update['message']['text']:
                    try:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='ID | USERNAME | MEDIA | FOLLOWERS | FOLLOWING\n'+Top10Followers() ))
                    except:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=u'Erro! Tente novamente mais tarde.' ))
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
