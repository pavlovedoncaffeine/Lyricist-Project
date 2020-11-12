#is_win = sys.platform.startswith('win')
# Spotify Client Credentials Object Initialzation
# spClientCred = spotipy.SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)#, proxies=None, requests_session=True, requests_timeout=None)

import sys
import requests
import spotipy
import threading
import json
import six

from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import *
from six.moves.BaseHTTPServer import HTTPServer

SPOTIFY_CLIENT_ID = '7b45f66cbae54e518a9fb2e5717e6e6d'
SPOTIFY_CLIENT_SECRET = '108a6846a16f47b5ba15ef306775396c'
SPOTIFY_REDIRECT = "http://localhost:8888/callback/"

# Class to create a test HTTP server on a seperate thread
# for oAuth2.0 response testing during dev.
class serverThread(threading.Thread):

    def __init__(self, server=None):
        self.server = server
        threading.Thread.__init__(self)

lyScope = 'user-read-playback-state'
# Spotify OAuth2.0 to authorize the web API token systems
spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT, state=None, scope=lyScope, username='dk_krypton', show_dialog=False))

# spawn second thread if required, to test server's redirect_uri and response codes beahviour
httptestServer = spotipy.oauth2.start_local_http_server(8888)
httpTestServerThread = serverThread(httptestServer)
httpTestServerThread.start() 

queryResult = spLyricist.current_user_playing_track()
# print("The result of the query:")
# print(queryResult)