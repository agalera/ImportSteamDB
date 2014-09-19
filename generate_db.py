import json
import requests
from threading import Thread, BoundedSemaphore
from pymongo import MongoClient


def get_json(url):
    try:
        return json.loads(requests.get(url).content)
    except:
        return None


def consigue(game):
    try:
        url = 'http://store.steampowered.com/api/appdetails/?appids='
        result = get_json('{}{}'.format(url, game['appid']))
        #platforms
        #voluntary no individual except
        platforms = []
        for x in result['platforms']:
            if result['platforms'][x]:
                platforms.append(x)
        result['platforms'] = platforms

        #categories
        categories = []
        try:
            for x in result['categories']:
                categories.append(x['description'])
        except:
            print "ko categories"
        try:
            for x in result['genres']:
                categories.append(x['description'])
        except:
            print "ko genres"
        result['categories'] = categories

        #supported_languages
        supported_languages = []
        try:
            for x in result['supported_languages'].split():
                supported_languages.append(x.strip())
        except:
            print "ko supported_languages"
        result['supported_languages'] = supported_languages
        db.games.insert(result)
        print "ok", game['appid']
    except:
        print "ko", game['appid']
    finally:
        pool_sema.release()

c = MongoClient()
db = c.Steam
db.games.drop()
url = 'http://api.steampowered.com/ISteamApps/GetAppList/v2?format=json'
lista = get_json(url)
pool_sema = BoundedSemaphore(100)
for game in lista["applist"]["apps"]:
    pool_sema.acquire()
    thread = Thread(target=consigue, args=(game, ))
    thread.start()
