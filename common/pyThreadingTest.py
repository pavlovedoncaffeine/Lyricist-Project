# multithreading practice python script - pavlovedoncaffeine (for Spotify Lyricist Project)
import time
import sys
import threading
import spotipy
import requests
import json
import six

from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import *
from six.moves.BaseHTTPServer import HTTPServer

serverThreadExitCode = 0
lyScope = 'user-read-playback-state'
SPOTIFY_CLIENT_ID = '7b45f66cbae54e518a9fb2e5717e6e6d'
SPOTIFY_CLIENT_SECRET = '108a6846a16f47b5ba15ef306775396c'
SPOTIFY_REDIRECT = "http://localhost:8888/callback/"

class localServerThread (threading.Thread):
    def __init__(self, name="Spotify OAuth2.0 Authentication Server", server=None):
        threading.Thread.__init__(self)
        self.server = server
        self.name = name

    def run(self):
        print ("Initializing " + self.name)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.shutdown()
            server.server_close()
            print (time.asctime() + " - Lyricist: Spotify OAuth2.0 Server shutting down.\n")


if __name__ == '__main__':
# Spotify OAuth2.0 to authorize the web API token systems
    spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT, state=None, scope=lyScope, username='dk_krypton', show_dialog=False))

    oAuthServer = spotipy.oauth2.start_local_http_server(8888)
    oAuthThread = localServerThread(oAuthServer)
    print(time.asctime() + " - Lyricist: Launching Spotify OAuth2.0 Service.")
    oAuthThread.start()

    query = spLyricist.current_user_playing_track()