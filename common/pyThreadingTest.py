# this is only really for Windows/Linux/MacOS overlay applications as spotify provides an iOS and Android SDK that doesn't require the Web API to get metadata for the player's state.
# multithreading oAuth2.0 python test script - pavlovedoncaffeine (for Spotify Lyricist Project)

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
#lyScope = 'user-read-currently-playing'    #Doesn't allow access to what the user's listening to in private mode, and still requires authorization. 
                                            # Could use some additional scope testing to see if any of them allow us to read the current track even in private mode
#lyScope = None  #If the user chooses not to share Authorize Spotify to share data with Lyricist, we can attempt to progress with just the implicitly available information when the user is *not* in private-mode

lyScope = None  # || (if user consider's authorization..) lyScope = 'user-read-currently-playing user-read-playback-position playlist-read-private'
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
    
    
    spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT, state=None, scope=lyScope, username='dk_krypton', show_dialog=False))
    query = spLyricist.currently_playing()      #query = spLyricist.user_playlist_is_following(playlist_id='7xB6mybJCHX92r3ZPS1FJ2', user_ids=['bluecan309'])
    

    if spLyricist is not None and query is not None:
        print (json.dumps(query, sort_keys=True, indent=4))
    else:
        print("Could not retrieve current playback information...")
    exit(200)

if __name__ == '__main__':
   main()