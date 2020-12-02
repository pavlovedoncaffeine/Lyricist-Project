# this is only really for Windows/Linux/MacOS overlay applications as spotify provides an iOS and Android SDK that doesn't require the Web API to get metadata for the player's state.
# multithreading oAuth2.0 python test script - pavlovedoncaffeine (for Spotify Lyricist Project)

import os
import sys
import time
import threading
import six
import requests
import json
import traceback
import pathlib
import spotipy
import azlyrics
import pyLogging
import lyricistSQL

# from pyLogging import *
# from lyricistSQL import *
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import *
from six.moves.BaseHTTPServer import HTTPServer

# serverThreadExitCode = 0
# lyScope = 'user-read-currently-playing'    #Doesn't allow access to what the user's listening to in private mode, and still requires authorization.
# Could use some additional scope testing to see if any of them allow us to read the current track even in private mode
# lyScope = None  #If the user chooses not to share Authorize Spotify to share data with Lyricist, we can attempt to progress with just the implicitly available information when the user is *not* in private-mode

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

LOGFILE = os.path.join(os.getcwd(), "common", "logs",
                       pyLogging.genLogfileName())
DATA_FOLDER = "E:\\Projects\\Lyricist\\Data"
lyrDB = lyricistSQL.lyricistDB()


class localServerThread (threading.Thread):
    def __init__(self, server=None, name='Spotify OAuth2.0 Authentication Server'):
        threading.Thread.__init__(self)
        print('Initializing...')
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
    except:
        raise AssertionError(
            "Invalid argument(s) to retrieve track list. Aborting operation.")
        return None
    queryResult = spLyr.playlist(plistID, fields='tracks(total)')
    total = queryResult['tracks']['total']
    trackList = []
    while index < total:
        queryResult = spLyr.playlist_tracks(
            plistID, fields='items(track(name, artists(name), album, id,explicit,duration_ms))', offset=index)['items']
        index += 100
        for val in queryResult:
            # track = {}
            song = val["track"]
            track = {
                'track_name': song["name"],
                'artists': ", ".join(artist["name"] for artist in song["artists"]),
                'album': song["album"]["name"],
                'spotify_trackID': song["id"],
                'apple_trackID': None,
                'bpm': None,
                'has_lyrics': False,
                'is_explicit': song["explicit"],
                'duration_ms': song["duration_ms"],
                'is_cover': None,
                'courtesy_of': "azlyrics.com",  # default during dev-testing
                'lyric_file': None,
            }

            # track["track_name"] = song["name"]
            # track["artists"] = ", ".join([
            #     artist["name"] for artist in song["artists"]])
            # track["album"] = song["album"]["name"]
            # track["bpm"] = None
            # track["spotify_trackID"] = song["id"]
            # track["apple_trackID"] = None
            # track["has_lyrics"] = False
            # track["is_explicit"] = song["explicit"]
            # track["duration_ms"] = song["duration_ms"]
            # track["is_cover"] = None
            # track["courtesy_of"] = None
            # track["lyric_file"] = None

            trackList.append(track)

    # print(json.dumps(trackList, indent=4))         # debugging
    # exit()
    return trackList


def saveLyrics(song=None, artists=None):
    if song is None or artists is None:
        return None
    artist = artists.split(', ')[0]
    print("\nArtist: " + artist + "\n")
    # invalid = '<>:"|?*'  # For Windows
    # for char in invalid:
    #     if char in song:
    #         song = song.replace(char, "")
    #     if char in artist:
    #         artist = artist.replace(char, "")

    lyricsAZ = azlyrics.lyrics(artist, song)
    if type(lyricsAZ) is dict:
        print(json.dumps(lyricsAZ, indent=4))
        raise Exception(
            "Error encountered while fetching lyrics: \n\t" + lyricsAZ['Error'])
    elif lyricsAZ is not None:  # if the lyrics are found, save it to a folder in "E:\Data\"
        artist_dir = os.path.join(DATA_FOLDER, artist)
        pathlib.Path(artist_dir).mkdir(parents=True, exist_ok=True)
        lyricsFilePath = os.path.join(artist_dir, song) + ".ly"
        try:
            with open(lyricsFilePath, 'x') as lyricsFile:
                lyricsFile.write(song + " - " + artists + "\n")
                for line in lyricsAZ:
                    lyricsFile.write(line)
                lyricsFile.write("\n***\n")  # EOF indicator for lyricist?
            # print("Lyricist: Lyrics for:\n\t" + song + " - " + artists +
            #      "\nhave been saved in the following directory: " + artist_dir + "\n")
            return lyricsFilePath
        except FileExistsError as exc:
            print("Lyricist: Lyrics for:\n\t" + song + " - " + artists +
                  "\nalready exist in the following data folder: " + artist_dir + "\n")
            print(traceback.format_exc())
            return None
    else:
        return False  # debugging... still-to-implement: search other databases such as musixmatch and genius etc etc to generate lyrics files


def main():
    with pyLogging.writeLog(open(LOGFILE, 'a')):
        # Spotify OAuth2.0 to authorize the web API token systems
        oAuthServer = spotipy.oauth2.start_local_http_server(port=8888)
        oAuthThread = localServerThread(oAuthServer)

        try:
            try:
                if oAuthThread is not None:
                    print(pyLogging.genTimestamp() +
                          'Lyricist: Launching Spotify OAuth2.0 Authorization Service.')
                    oAuthThread.start()
            except Exception as exc:
                print(pyLogging.genTimestamp() +
                      'Lyricist: Spotify OAuth2.0 Authorization Service could not be initialized.')
                print(traceback.format_exc())

        except KeyboardInterrupt:
            oAuthThread.join(1)
            oAuthServer.shutdown()
            oAuthServer.server_close()
            raise PermissionError(pyLogging.genTimestamp() +
                                  'Lyricist: Spotify OAuth2.0 Server Initialization Aborted.')
            print(traceback.format_exc())

        finally:
            oAuthThread.join(1)
            oAuthServer.shutdown()
            oAuthServer.server_close()
            print(pyLogging.genTimestamp() +
                  'Lyricist: Spotify OAuth2.0 Server shutting down')

        spLyricist = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET,
                                                               redirect_uri=SPOTIFY_REDIRECT, state=None, scope=lyScope, username='dk_krypton', show_dialog=True))
        # bring the house down : dk_krypton
        test_playlist = '6jviAN7MIgh36bLHEPI4DL'
        if spLyricist is not None:
            playlistTracks = getTracksFromPlaylist(spLyricist, test_playlist)

            # 1. for-each through list of tracks in playlist # 1. SELECT track, artists from lyricist_tracks (lyricistDB.selectRow(self, track_name, artists)) # to be implemented
            # 2. check if each track in playlist exists in database, and if it has lyrics
            # 3. if yes, return lyricFile from db's storage
            # 4. (done) otherwise, run saveLyrics(song, artists)
            for track in playlistTracks:
                print("Testing...")
                print(json.dumps(track, indent=4))
                try:
                    lyricsFile = saveLyrics(
                        track["track_name"], track["artists"])
                    if lyricsFile is not None:
                        track["has_lyrics"] = True
                        track["lyric_file"] = lyricsFile
                        #track["courtesy_of"] = "azLyrics.com"
                        if lyrDB.insertTrackFromDict(track):
                            print(track["track_name"] + " - " + track["artists"] +
                                  ".\nLyricist: Successfully stored track details in database.")
                        else:
                            print("Lyricist: Could not store data in database.")
                except AssertionError as exc:
                    print(traceback.format_exc())
        else:
            raise PermissionError(pyLogging.genTimestamp() +
                                  'Lyricist: Could not retrieve playlist.\nPlease ensure that Spotify is not in \'Private Mode\'')

    lyrDB.cursor.close()
    lyrDB.close()


if __name__ == '__main__':
    main()
