# this is only really for Windows/Linux/MacOS overlay applications as spotify provides an iOS and Android SDK that doesn't require the Web API to get metadata for the player's state.
# multithreading oAuth2.0 python test script - pavlovedoncaffeine (for Spotify Lyricist Project)

import os
import sys, time, threading
import six, requests, json
import traceback
import spotipy
import azlyrics

from pyLogging import *
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
        line = 'init'
        while line:
            line = secretsFile.readline()
            words = line.split(' ')
            if words[0] == 'SPOTIFY_CLIENT_ID':
                SPOTIFY_CLIENT_ID = words[1].strip()
            elif words[0] == 'SPOTIFY_CLIENT_SECRET':
                SPOTIFY_CLIENT_SECRET = words[1].strip()
    
LOGFILE = os.path.join(os.getcwd(), "common", "logs", genLogfileName())
DATA_FOLDER = "E:\\Projects\\Lyricist\\Data\\"

class localServerThread (threading.Thread):
    def __init__(self, server=None, name='Spotify OAuth2.0 Authentication Server'):
        threading.Thread.__init__(self)
        print ('Initializing...')
        self.server = server
        self.name = name

    def run(self):
        self.server.serve_forever()


def getTracksFromPlaylist(spLyr=None, plistID=None):
    queryResult = None
    index = 0
    total = 0
    
    try:
        assert(spLyr is not None)
        assert(plistID is not None)
    except exc:
        raise AssertionError("Invalid argument(s) to retrieve track list. Aborting operation.")
        return None

    queryResult = spLyr.playlist(plistID, fields='tracks(total)')
    total = queryResult['tracks']['total']

    trackList = []    
    while index < total:
        queryResult = spLyr.playlist_tracks(plistID, fields='items(track(name, artists(name),id,explicit,duration_ms))', offset=index)['items']
        index += 100
        for val in queryResult:
            song = val["track"]
            track = {}
            track["name"] = song["name"]
            track["artists"] = ', '.join([artist["name"] for artist in song["artists"]])
            track["spotify_ID"] = song["id"]
            track["explicit"] = song["explicit"]
            track["duration_ms"] = song["duration_ms"]
            trackList.append(track)

    #print(json.dumps(trackList, indent=4))         # debugging
    return trackList



# To-do: November 21st, 2020 implement a rudimentary system to pull lyrics and write to file in the Data Folder.s
# def getLyrics(song=None, artist=None):
# return None    


def main():
    
    with writeLog(open(LOGFILE, 'a')):
        
        oAuthServer = spotipy.oauth2.start_local_http_server(port=8888)     # Spotify OAuth2.0 to authorize the web API token systems
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
        
        if spLyricist is not None:
            queryResult = getTracksFromPlaylist(spLyricist, '6jviAN7MIgh36bLHEPI4DL')
            print(json.dumps(queryResult, indent=4))
            exit()
        else:
            raise PermissionError(genTimestamp() + 'Lyricist: Could not retrieve playlist.\nPlease ensure that Spotify is not in \'Private Mode\'')

if __name__ == '__main__':
   main()