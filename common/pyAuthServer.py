# this is only really for Windows/Linux/MacOS overlay applications as spotify provides an iOS and Android SDK that doesn't require the Web API to get metadata for the player's state.
# multithreading oAuth2.0 python test script - pavlovedoncaffeine (for Spotify Lyricist Project)

import os
import sys, time, threading
import six, requests, json
import traceback
from pyLogging import *
import spotipy


from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import *
from six.moves.BaseHTTPServer import HTTPServer

#serverThreadExitCode = 0
#lyScope = 'user-read-currently-playing'    #Doesn't allow access to what the user's listening to in private mode, and still requires authorization. 
                                            # Could use some additional scope testing to see if any of them allow us to read the current track even in private mode
#lyScope = None  #If the user chooses not to share Authorize Spotify to share data with Lyricist, we can attempt to progress with just the implicitly available information when the user is *not* in private-mode

lyScope = 'user-read-currently-playing user-read-playback-position playlist-read-private'
SPOTIFY_REDIRECT = "http://localhost:8888/callback/"
SPOTIFY_CLIENT_ID = None
SPOTIFY_CLIENT_SECRET = None

secrets = os.path.join(os.getcwd(), "common", "lyricistSecrets.txt")
with open(secrets, 'r') as secretsFile:
    if secretsFile is not None:
        line = '<starting_file_read>'
        while line:
            line = secretsFile.readline()
            words = line.split(' ')
            if words[0] == 'SPOTIFY_CLIENT_ID':
                SPOTIFY_CLIENT_ID = words[1].strip()
            elif words[0] == 'SPOTIFY_CLIENT_SECRET':
                SPOTIFY_CLIENT_SECRET = words[1].strip()
    
LOGFILE = os.path.join(os.getcwd(), "common", "logs", genLogfileName())

class localServerThread (threading.Thread):
    def __init__(self, server=None, name='Spotify OAuth2.0 Authentication Server'):
        threading.Thread.__init__(self)
        print ('Initializing...')
        self.server = server
        self.name = name

    def run(self):
        self.server.serve_forever()


def main():
    
    with writeLog(open(LOGFILE, 'a')):
        
        # Spotify OAuth2.0 to authorize the web API token systems
        oAuthServer = spotipy.oauth2.start_local_http_server(port=8888)
        oAuthThread = localServerThread(oAuthServer)
        try:
            try:
                if oAuthThread is not None:
                    print(genTimestamp() + 'Lyricist: Launching Spotify oAuth2 Authorization Service.')
                    oAuthThread.start()
            except Exception as exc:
                print(genTimestamp() + 'Lyricist: Spotify oAuth2 Authorization Service could not be initialized.')
                traceback.format()

        except KeyboardInterrupt:
            oAuthThread.join(1)
            oAuthServer.shutdown()
            oAuthServer.server_close()
            raise PermissionError(genTimestamp() + 'Lyricist: Spotify OAuth2.0 Server Initialization Aborted.')
            traceback.format()
            
        finally:
            oAuthThread.join(1)
            oAuthServer.shutdown()
            oAuthServer.server_close()
            print (genTimestamp() + 'Lyricist: Spotify oAuth2 Server shutting down')
        
        spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET, redirect_uri=SPOTIFY_REDIRECT, state=None, scope=lyScope, username='dk_krypton', show_dialog=False))
        query = spLyricist.currently_playing()      #query = spLyricist.user_playlist_is_following(playlist_id='7xB6mybJCHX92r3ZPS1FJ2', user_ids=['bluecan309'])
        
        if spLyricist is not None and query is not None:
            print (json.dumps(query, sort_keys=True, indent=4))
        else:
            #print()
            raise PermissionError(genTimestamp() + 'Lyricist: Could not retrieve current playback information. Please ensure that Spotify is in \'Private Mode\'')

if __name__ == '__main__':
   main()