# -*- coding: utf-8 -*-
from sinchsms import SinchSMS # pip install sinchsms
import tokens
import pickle # pip install pickle
import json
import requests
import os
from time import sleep

if os.path.isfile('last_update_sms.txt') == True:
    file = open('last_update_sms.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % tokens.telegram_bot_sms

while True:
    get_updates = json.loads(requests.get(url + 'getUpdates').content)
    for update in get_updates['result']:
        if last_update < update['update_id']:
            last_update = update['update_id']
            file = open('last_update_sms.txt', 'w')
            pickle.dump(last_update, file)
            file.close()
            print(update['message']['text'])
            try:
                if u'/start' in update['message']['text']:
                    help_bot = u'Olá\nPara enviar um SMS digite /enviarSMS 11999999999 Olá Tudo Bem?'
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=help_bot ))
                if u'/enviarSMS' in update['message']['text']:
                    keyword = update['message']['text'].split(' ', 2)
                    number = '+'+keyword[1]
                    message = keyword[2]
                    client = SinchSMS(tokens.key_sinch, tokens.secret_sinch)
                    client.send_message(number, message)
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text="Enviando '%s' para %s" % (message, number) ))
            except KeyError as e:
                print(e)
                continue
    sleep(3)
