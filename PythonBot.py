# -*- coding: utf-8 -*-
import requests
import json
from time import sleep
import pickle
import os
import random
import tokens

if os.path.isfile('last_update.txt') == True:
    file = open('last_update.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % tokens.telegram_bot

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
                if u'manda stack' in update['message']['text']:
                    random_stackoverflow = json.loads(requests.get('https://api.stackexchange.com/2.2/search?pagesize=100&order=desc&min=1404172800&max=1435968000&sort=activity&tagged=python&site=stackoverflow').content)
                    rand_id = random.randint(1, 99)
                    send_random = '%s\n%s' % (random_stackoverflow['items'][rand_id]['title'], random_stackoverflow['items'][rand_id]['link'])
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=send_random ))
                if u'sobre python' in update['message']['text']:
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='https://pt.wikipedia.org/wiki/Python' ))
            except KeyError as e:
                print(e)
                continue
    sleep(3)
