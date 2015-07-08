# -*- coding: utf-8 -*-
from datetime import datetime
import string
import requests
import json
from time import sleep
import pickle
import os
import random
import tokens
from twitter import Twitter, OAuth  # easy_install twitter_oauth
import urllib2
from xml.dom import minidom

def FacebookPost():
    pages = ['pythonbrasil', '1658435974378579', 'minutopython']
    url = "https://graph.facebook.com/%s/posts?limit=50&access_token=%s" % (random.choice(pages), tokens.graph_api_token)
    json_data = json.loads(requests.get(url).content)
    random_post = random.randint(0, len(json_data['data']))
    if 'message' in json_data['data'][random_post]:
        content = json_data['data'][random_post]['message']
    message_id = json_data['data'][random_post]['id']
    org_id = message_id.split('_')[0]
    status_id = message_id.split('_')[1]
    post_link = 'https://www.facebook.com/%s/posts/%s' % (org_id, status_id)
    return '%s\n%s' % (content,post_link)

def Rand_Posts():
    blogs_feeds = ['http://pythonclub.com.br/feeds/all.atom.xml', 'http://brsource.com.br/blog/feed/']
    random_blog = random.choice(blogs_feeds)
    posts_source = urllib2.urlopen(random_blog)
    results = posts_source.read()
    doc = minidom.parseString(results)
    if random_blog == blogs_feeds[0]:
        posts = doc.getElementsByTagName('entry')
        random_post = random.randint(0, len(posts))
        try:
            title = posts[random_post].getElementsByTagName('title')[0].firstChild.nodeValue
            link = posts[random_post].getElementsByTagName('link')[0].getAttribute('href')
            return title+'\n'+link
        except IndexError:
            Rand_Posts()
    elif random_blog == blogs_feeds[1]:
        posts = doc.getElementsByTagName('item')
        random_post = random.randint(0, len(posts))
        try:
            title = posts[random_post].getElementsByTagName('title')[0].firstChild.nodeValue
            link = posts[random_post].getElementsByTagName('link')[0].firstChild.nodeValue
            if title.lower().find('python') != -1:
                return title+'\n'+link
            else:
                Rand_Posts()
        except IndexError:
            Rand_Posts()

def quiz(answer):
    questions_json = json.load(open('questions.json', 'r'))
    question_info = questions_json[datetime.now().hour]
    optionLetters = string.ascii_lowercase[:len(question_info['options'])]
    options_output = '\n'.join('%s: %s' % (letter, answer) for letter, answer in zip(optionLetters, question_info['options']))
    if len(answer) > 0:
        if answer == optionLetters[question_info['correct_option']]:
            return 'Acertou!\n%s\nResposta correta: %s' % (question_info['question'], question_info['options'][question_info['correct_option']])
        elif answer not in optionLetters:
            return u'Opção não existe!'
        else:
            return 'Errou'
    else:
        return u'%s\n%s\n\nEnvie /respQuiz "letra" sem aspas.' % (question_info['question'], options_output)

twitter = Twitter(auth=OAuth(tokens.access_key, tokens.access_secret, tokens.consumer_key, tokens.consumer_secret))

if os.path.isfile('last_update.txt') == True:
    file = open('last_update.txt', 'r')
    last_update = pickle.load(file)
else:
    last_update = 0

url = 'https://api.telegram.org/bot%s/' % tokens.telegram_bot_python

while True:
    get_updates = json.loads(requests.get(url + 'getUpdates?offset='+str(last_update)).content)
    for update in get_updates['result']:
        if last_update < update['update_id']:
            last_update = update['update_id']
            file = open('last_update.txt', 'w')
            pickle.dump(last_update, file)
            file.close()
            try:
                print(update['message']['text'])
            except:
                continue
            try:
                if u'/start' in update['message']['text']:
                    help_bot = u'Olá\nComandos disponíveis:\n/enviaFace: Envia um post aleatório de páginas sobre Python.\n/enviaArtigo: Envia um artigo aletório sobre Python & cia.\n/enviaGithub: Envia um repo de python aleatório.\n/buscarGithub "Texto": Digite um texto para buscar um repo no github sem aspas.\n/enviaStack: Envia um stackoverflow randomico sobre Python.\n/sobrePython: Envia artigo da Wikipedia sobre Python.\n/enviaTwitter: Envia um tweet mais recente com a hashtag Python.'
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
                if u'/enviaArtigo' in update['message']['text']:
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=Rand_Posts() ))
                if u'/enviaQuiz' in update['message']['text']:
                    requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=quiz('') ))
                if u'/respQuiz' in update['message']['text']:
                    keyword = update['message']['text'].split(' ', 1)
                    try:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=quiz(keyword[1]) ))
                    except IndexError:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Envie uma opção' ))
                        continue
                if u'/enviaFace' in update['message']['text']:
                    try:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text=FacebookPost() ))
                    except:
                        requests.get(url + 'sendMessage', params=dict(chat_id=update['message']['chat']['id'], text='Facebook API temporariamente indisponível :(' ))
                        continue
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
