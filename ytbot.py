from datetime import datetime, time, date, timedelta
from time import sleep
import json
import colector
import editor
import sender
import locale

locale.setlocale(locale.LC_ALL, '')

with open('config.json', 'r') as fconfig:
    config = json.load(fconfig)

singleRun = True
while config['ytbot']['timed'] or singleRun:

    if config['ytbot']['timed']:
        now = datetime.now()
        then = datetime.combine(
            date.today() if time.fromisoformat(config['ytbot']['time']) > now.time()
            else date.today() + timedelta(days=1),
            time.fromisoformat(config['ytbot']['time'])
        )

        delta = then - now
        print(f'waiting for {then}')
        sleep(delta.total_seconds())

    today = date.today()
    videoDate = today - timedelta(days=1) if config['ytbot']['yesterday'] else today
    clips = {}

    for game in config['clips']['games']:

        print(f'searching for {game} clips...')
        clips[game] = colector.search(
            game,
            config['clips']['period'],
            config['clips']['language'],
            config['twitch']['clientId']
        )

    for game in clips.keys():
        config['videos']['episode'] += 1

        print(f'colecting {game} clips...')
        downloadedClips = []
        duration = 0.0
        for clip in clips[game]:
            if duration <= config['videos']['minDuration']:
                clip['path'] = colector.colect(f'clips/{str(today)}/{game}', clip)
                duration += clip['duration']
                downloadedClips.append(clip)
            else:
                break
        
        titleScaffolding = config['videos']['title'].replace('}', '{').split('{')
        title = ''.join([str(eval(titleScaffolding[x])) if x % 2 != 0 else titleScaffolding[x] for x in range(len(titleScaffolding))])

        descriptionScaffolding = config['videos']['description'].replace('}', '{').split('{')
        description = ''.join([str(eval(descriptionScaffolding[x])) if x % 2 != 0 else descriptionScaffolding[x] for x in range(len(descriptionScaffolding))])

        tagsScaffolding = [tag.replace('}', '{').split('{') for tag in config['videos']['tags']]
        tags = [''.join([str(eval(tagScaffolding[x])) if x % 2 != 0 else tagScaffolding[x] for x in range(len(tagScaffolding))]) for tagScaffolding in tagsScaffolding]

        print('compiling clips...')
        video = editor.makeVideo(
            f'output/{str(today)}/{game}',
            title,
            [clip['path'] for clip in downloadedClips],
            config['videos']['transitionInFiles'],
            config['videos']['transitionOutFiles'],
            config['videos']['width'],
            config['videos']['height'],
            config['videos']['fps']
        )

        print('getting youtube access token...')
        accessToken = sender.getAccessToken(
            config['youtube']['clientId'],
            config['youtube']['clientSecret'],
            config['youtube']['refreshToken']
        )

        print('getting upload session URI...')
        sessionURI = sender.getSessionURI(
            title,
            video,
            description,
            tags,
            config['videos']['categoryId'],
            config['videos']['privacyStatus'],
            accessToken
        )

        print('uploading video...')
        response = sender.uploadVideo(video, sessionURI, accessToken)

    with open('config.json', 'w') as fconfig:
        json.dump(config, fconfig, indent=4, separators=(',', ' : '))

    singleRun = False
