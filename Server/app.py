from flask import Flask, json
from flask_cors import CORS
import requests
import os.path, os
import random

TOKEN_URL = 'https://accounts.spotify.com/api/token'

userTokensJSON = None
with open('static/usertokens.json') as usertokensFile:
    userTokensJSON = json.load(usertokensFile)

CLIENT_ID = userTokensJSON.get('client_id')
CLIENT_SECRET = userTokensJSON.get('client_secret')

app = Flask(__name__)
CORS(app)

def reformatTrackJSON(track):
    return {
        'artist': track.get('artists')[0].get('name'),
        'track' : track.get('name'),
        'album_image_url': track.get('album').get('images')[0].get('url'),
        'preview_url': track.get('preview_url')
    }

class Server:
    def __init__(self):

        with open('static/genres.json') as genresFile:
            self.genres = json.load(genresFile)
        
        # Access Token Lasts 1 Hour. Therefore it is stored in a file and is reused until it expires.
        # When it is expired, a new one is acquired.
        if os.path.isfile('static/accesstoken.txt'):
            self.loadToken()
        else:
            self.access_token = self.getAccessToken()
            self.saveToken()

    def getAccessToken(self):
        payload = {
            'grant_type': 'client_credentials',
        }
        res = requests.post(TOKEN_URL, auth=(CLIENT_ID, CLIENT_SECRET), data=payload)
        return res.json().get('access_token')

    def loadToken(self):
        with open('static/accesstoken.txt', 'r') as tokenFile:
            self.access_token = tokenFile.read()

    def saveToken(self):
        with open('static/accesstoken.txt', 'w') as tokenFile:
            tokenFile.write(self.access_token)

    # Decided not to use Top Tracks of An Artist because Market field is required in it and I want an international search.
    def searchRequest(self, artist):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        params = {
            'q': 'artist:' + artist,
            'type': 'track',
            'limit': 50
        }
        return requests.get(f'https://api.spotify.com/v1/search', headers=headers, params=params)
    
    def getPopularTracks(self, artist):
        searchResult = self.searchRequest(artist)
        if (searchResult.status_code != 200):
            # Refresh Access Token And Retry If Expired
            self.access_token = self.getAccessToken()
            self.saveToken()
            searchResult = self.searchRequest(artist)
            if (searchResult.status_code != 200):
                raise Exception("Could Not Get")

        return searchResult.json().get('tracks').get('items')
    
    def filterAndSort(self, top50, artist):
        sorted50 = sorted(top50, key=lambda item: item.get('popularity'),reverse=True)
        # Check If Artist Name is Correct
        filteredWrongArtists = [item for item in sorted50 if item.get('artists')[0].get('name').lower() == artist.lower()]
        # In case if name check failed because of character mismatch.
        if (len(filteredWrongArtists) == 0):
            return sorted50[:10]
        else:
            return filteredWrongArtists[:10]

    def getRandomArtist(self, genre):
        genreArtists = self.genres.get(genre)
        if (genreArtists is None):
            return None
        return random.choice(genreArtists)
    
    def getPopularInGenre(self, genre):
        randomArtist = self.getRandomArtist(genre)
        if (randomArtist is None):
            return None
        filtered10 =  self.filterAndSort(self.getPopularTracks(randomArtist), randomArtist)
        return [reformatTrackJSON(item) for item in filtered10]


server = Server()

@app.route('/tracks/<genre>', methods=['GET'])
def index(genre):
    queryResult = server.getPopularInGenre(genre)
    if (queryResult is None):
        return json.dumps({ "error": "No Track Found" }), 500
    else:
        return json.dumps(queryResult)

if __name__ == "__main__":
    app.run(debug=True)