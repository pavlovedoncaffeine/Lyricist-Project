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

#serverThreadExitCode = 0
lyScope = 'user-read-playback-state'
SPOTIFY_CLIENT_ID = '7b45f66cbae54e518a9fb2e5717e6e6d'
SPOTIFY_CLIENT_SECRET = '108a6846a16f47b5ba15ef306775396c'
SPOTIFY_REDIRECT = "http://localhost:8888/callback/"

class localServerThread (threading.Thread):
    def __init__(self, server=None, name="Spotify OAuth2.0 Authentication Server"):
        threading.Thread.__init__(self)
        print ("Initializing...")
        self.server = server
        self.name = name

    def run(self):
        self.server.serve_forever()


def main():
    # Spotify OAuth2.0 to authorize the web API token systems
    oAuthServer = spotipy.oauth2.start_local_http_server(port=8888)
    oAuthThread = localServerThread(oAuthServer)

    try:
        if oAuthThread is not None:
            print(time.asctime() + " - Lyricist: Launching Spotify OAuth2.0 Service.")
            oAuthThread.start()
        else:
            print(time.asctime() + " - Lyricist: Spotify Authorization thread was not launched. Aborting.\n")
            exit(400)

    except KeyboardInterrupt:
        oAuthThread.join(1)
        oAuthServer.shutdown()
        oAuthServer.server_close()
        print (time.asctime() + " - Lyricist: Spotify OAuth2.0 Server shutting down.\n")
        
    finally:
        oAuthThread.join(1)
        oAuthServer.shutdown()
        oAuthServer.server_close()
        print (time.asctime() + " - Lyricist: Spotify OAuth2.0 Server shutting down.\n")
    
    #to-do: see if the Client_secret can be omitted from the SpotifyOAuth initialization in the below statement. If yes, then we ought to be in business and can be erased from the git repo
    spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT, state=None, scope=lyScope, username='dk_krypton', show_dialog=True))
    query = spLyricist.currently_playing()

    if spLyricist is not None and query is not None:
        print (json.dumps(query, sort_keys=True, indent=4))
        exit(43)
    else:
        print("Could not retrieve current playback information...")
        exit(1300135)

if __name__ == '__main__':
   main()