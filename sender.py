import requests as http
import json
import os

def getAccessToken(clientId, clientSecret, refreshToken):

    body = {
        'client_id' : clientId,
        'client_secret' : clientSecret,
        'refresh_token' : refreshToken,
        'grant_type' : 'refresh_token'
    }

    return http.post('https://accounts.google.com/o/oauth2/token', data=body).json()['access_token']

def getSessionURI(title, path, description, tags, categoryId, privacyStatus, accessToken):
	body = json.dumps({
		"snippet": {
			"title": title,
			"description": description,
			"tags": tags,
			"categoryId": categoryId
		},
		"status": {
			"privacyStatus": privacyStatus,
			"license": "youtube"
		}
	})

	header = {
	    'Authorization' : f'Bearer {accessToken}',
	    'Content-Lenght' : str(len(body)),
	    'Content-Type' : 'application/json; charset=UTF-8',
	    'X-Upload-Content-Length' : str(os.path.getsize(path)),
		'X-Upload-Content-Type' : 'video/*'
	}

	r =  http.post('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status,contentDetails', headers=header, data=body)
	print(r.headers)
	return r.headers['Location']

def uploadVideo(path, sessionURI, accessToken):
	header = {
        'Authorization' : f'Bearer {accessToken}',
        'Content-Lenght' : str(os.path.getsize(path)),
        'Content-Type' : 'video/*',
    }
	video = open(path, 'rb')

	return http.post(sessionURI, data=video)