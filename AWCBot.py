# -*- coding: utf-8 -*-
import pickle # pip install pickle
import json
import urllib2
from bs4 import BeautifulSoup # pip install beautifulsoup4
import requests
import os
from time import sleep

if os.path.isfile('last_update.txt') == True:
    file = open('last_update.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % 'BOT_TOKEN_HERE'

while True:
    get_updates = json.loads(requests.get(url + 'getUpdates').content)
    for update in get_updates['result']:
        if last_update < update['update_id']:
            last_update = update['update_id']
            file = open('last_update.txt', 'w')
            pickle.dump(last_update, file)
            file.close()
            print(update['message']['text'])
            try:
                if u'/metar' in update['message']['text']:
                    keyword = update['message']['text'].split(' ', 1)
                    url_calling = 'http://aviationweather.gov/metar/data?ids='+keyword[1]+'&format=raw&date=0&hours=0'
                    page = urllib2.urlopen(url_calling).read()
                    bsoup = BeautifulSoup(page)
                    result = bsoup.find('code').text
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=result ))
                if u'/taf' in update['message']['text']:
                    keyword = update['message']['text'].split(' ', 1)
                    url_calling = 'http://aviationweather.gov/taf/data?ids='+keyword[1]+'&format=raw&submit=Get+TAF+data'
                    page = urllib2.urlopen(url_calling).read()
                    bsoup = BeautifulSoup(page)
                    result = bsoup.find('code').text
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=result ))
            except:
                requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Nothing found.' ))

    sleep(3)
