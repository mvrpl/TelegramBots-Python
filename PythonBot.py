# -*- coding: utf-8 -*-
import requests
import json
from time import sleep
import pickle
import os
import random
import tokens
from twitter import Twitter, OAuth  # easy_install twitter_oauth

twitter = Twitter(auth=OAuth(tokens.access_key, tokens.access_secret, tokens.consumer_key, tokens.consumer_secret))

if os.path.isfile('last_update.txt') == True:
    file = open('last_update.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % tokens.telegram_bot_python

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
                if u'/start' in update['message']['text']:
                    help_bot = u'Olá\nComandos disponíveis:\n/enviaGithub: Envia um repo de python aleatório.\n/buscarGithub "Texto": Digite um texto para buscar um repo no github sem aspas.\n/enviaStack: Envia um stackoverflow randomico sobre Python.\n/sobrePython: Envia artigo da Wikipedia sobre Python.\n/enviaTwitter: Envia um tweet mais recente com a hashtag Python.'
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=help_bot ))
                if u'/enviaStack' in update['message']['text']:
                    try:
                        random_stackoverflow = json.loads(requests.get('https://api.stackexchange.com/2.2/search?pagesize=100&order=desc&sort=activity&tagged=python&site=stackoverflow').content)
                    except requests.ConnectionError:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Stack Overflow temporariamente indisponível :(' ))
                        continue
                    rand_id = random.randint(0, 99)
                    send_random = '%s\n%s' % (random_stackoverflow['items'][rand_id]['title'], random_stackoverflow['items'][rand_id]['link'])
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=send_random ))
                if u'/sobrePython' in update['message']['text']:
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='https://pt.wikipedia.org/wiki/Python' ))
                if u'/enviaTwitter' in update['message']['text']:
                    results = twitter.search.tweets(q='"#python"')
                    if 'errors' in results:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Twitter temporariamente indisponível :(' ))
                        continue
                    last_tweet = "%s:\n%s" % (results["statuses"][0]["user"]["screen_name"], 'https://twitter.com/'+results["statuses"][0]["user"]["screen_name"]+'/status/'+results["statuses"][0]["id_str"])
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=last_tweet ))
                if u'/enviaGithub' in update['message']['text']:
                    git_repos = json.loads(requests.get('https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc').content)
                    rand_id = random.randint(0, 29)
                    send_github = '%s\n%s' % (git_repos['items'][rand_id]['description'], git_repos['items'][rand_id]['html_url'])
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=send_github ))
                if u'/buscarGithub' in update['message']['text']:
                    keyword = update['message']['text'].split(' ', 1)
                    try:
                        git_repos_search = json.loads(requests.get('https://api.github.com/search/repositories?q='+keyword[1]+'+language:python&sort=stars&order=desc').content)
                    except IndexError:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Nada Encontrado' ))
                        continue
                    rand_id = random.randint(0, len(git_repos_search['items']))
                    try:
                        send_github = '%s\n%s' % (git_repos_search['items'][rand_id]['description'], git_repos_search['items'][rand_id]['html_url'])
                    except IndexError:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Nada Encontrado' ))
                        continue
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=send_github ))
            except KeyError as e:
                print(e)
                continue
    sleep(3)
