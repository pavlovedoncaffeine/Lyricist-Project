# test script to correctly enable spotify OAuth2 functionality when looking up lyrics


# environment variables/ path variables
# Windows/UNIX
# SET/export SPOTIPY_CLIENT_ID=7b45f66cbae54e518a9fb2e5717e6e6d
# SET/export SPOTIPY_CLIENT_SECRET=108a6846a16f47b5ba15ef306775396c

SPOTIFY_CLIENT_ID = '7b45f66cbae54e518a9fb2e5717e6e6d'
SPOTIFY_CLIENT_SECRET = '108a6846a16f47b5ba15ef306775396c'
SPOTIFY_REDIRECT = 'http://127.0.0.1:8080/'

# GET https://api.spotify.com/v1/me/player/currently-playing



import sys
import requests
import spotipy
import json
from spotipy.oauth2 import  SpotifyOAuth

#is_win = sys.platform.startswith('win')

lyScope = 'user-read-playback-state'
spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT))

queryResult = spLyricist.current_user_playing_track()

for res in queryResult:
    print(res)