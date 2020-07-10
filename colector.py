import requests as http
import os

def search(game, period, language, clientId):

    headers = {
        'Client-ID' : clientId,
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }

    r = http.get(f'https://api.twitch.tv/kraken/clips/top?game={game}&language={language}&period={period}&limit=100', headers=headers)
    while r.status_code == 500:
        print('an error occured. retrying...')
        r = http.get(f'https://api.twitch.tv/kraken/clips/top?game={game}&language={language}&period={period}&limit=100', headers=headers)
    clips = []

    rawClips = r.json()['clips']
    for rawClip in rawClips:
        clip = {}
        clip['id'] = rawClip['slug']
        clip['streamer'] = rawClip['broadcaster']['display_name']
        clip['channel_url'] = rawClip['broadcaster']['channel_url']
        clip['duration'] = rawClip['duration']
        clip['link'] = rawClip['thumbnails']['medium'].split("-preview",1)[0] + ".mp4"
        clips.append(clip)

    return clips

def colect(dir, clip):
    if not os.path.isdir(dir):
        os.makedirs(dir)
    path = f'{dir}/{clip["id"]}.mp4'
    data = http.get(clip['link'])
    with open(path, 'wb') as file:
        file.write(data.content)

    return path