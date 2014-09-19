import json
import requests
from threading import Thread, BoundedSemaphore
from pymongo import MongoClient

c = MongoClient()
db = c.Steam
db.games.drop()
def get_json(url):
    try:
        return json.loads(requests.get(url).content)
    except:
        return None

lista = get_json('http://api.steampowered.com/ISteamApps/GetAppList/v2?format=json')
pool_sema = BoundedSemaphore(100)
def consigue(game):
    try:
        result = get_json('http://store.steampowered.com/api/appdetails/?appids='+str(game['appid']))[str(game['appid'])]['data']
        #platforms
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
            print "falla categories"
        try:
            for x in result['genres']:
                categories.append(x['description'])
        except:
            print "falla genres"
        result['categories'] = categories

        #supported_languages
        supported_languages = []
        try:
            for x in result['supported_languages'].split():
                supported_languages.append(x.strip())
        except:
            print "falla supported_languages"
        result['supported_languages'] = supported_languages
        db.games.insert(result)
        print "ok", game['appid']
    except:
        print "fallo", game['appid']
    finally:
        pool_sema.release()

for game in lista["applist"]["apps"]:
    pool_sema.acquire()
    thread = Thread(target = consigue, args = (game, ))
    thread.start()