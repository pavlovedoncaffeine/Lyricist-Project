import os
import traceback
#from datetime import date, datetime
import mysql.connector
from mysql.connector import errorcode

# JSON structure:
# { 'track_name' : <String/varchar>,
#   'artists'    : <String/varchar>,
#   'album'      : <String/varchar>,
#   'is_explicit': <Boolean>,
#   'duration_ms': <Int> UNSIGNED,
#   'spotify_trackID': <String/varchar>,
#   'apple_trackID'  : <String/varchar>,
#   'bpm'        : <Int> UNSIGNED,
#   'is_cover'   : <Boolean>,
#   'has_lyrics' : <Boolean>,
#   'courtesy_of': <String/varchar>,
#   'lyric_file' : <String/varchar>
# }


def select_file(track_name=None, artists=None):
    return


class lyricistDB:

    def __init__(self):
        self.lySQL = None
        self.cursor = None

        try:
            self.lySQL = mysql.connector.connect(
                user='pavlovedoncaffeine', password='C0mput3r!', host='127.0.0.1', port=3306, database='LyricistDB')
            self.cursor = lySQL.cursor()
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Error authorizing access to the Lyricist database.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Lyricist: Database not reachable.")
            print(traceback.format_exc()+"\n")

    def updateTrack(self, track=None):
        if track is None:
            return False
        try:
            updateRow = ("UPDATE lyricist_tracks SET album = %s, is_explicit = %s, duration_ms = %s, spotify_trackID = %s, apple_trackID = %s, bpm = %s, is_cover = %s, has_lyrics = %s, courtesy_of = %s, lyric_file = %s "
                         "WHERE track_name = %s AND artists = %s")
            self.cursor.execute(updateRow, track)
            assert(commitToDB())
            return True
        except:
            print(traceback.format_exc())
            return False

    def insertTrackFromDict(self, track=None):
        if track is None:
            return False
        try:
            insertRow = ("INSERT INTO lyricist_tracks "
                         "(track_name, artists, album, is_explicit, duration_ms, spotify_trackID, apple_trackID, bpm, is_cover, has_lyrics, courtesy_of, lyric_file) "
                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
            self.cursor.execute(insertRow, track)
            assert(commitToDB())
            return True
        except:
            print(traceback.format_exc())
            return False

    def insertTrackDetails(self, track_name, artists, album=None, is_explicit=False, duration_ms=None, spotify_trackID=None, apple_trackID=None, is_cover=False, has_lyrics=False, courtesy_of=False, lyric_file=None):
        try:
            insertRow = ("INSERT INTO lyricist_tracks "
                         "(track_name, artists, album, is_explicit, duration_ms, spotify_trackID, apple_trackID, bpm, is_cover, has_lyrics, courtesy_of, lyric_file) "
                         "VALUES (%(track_name)s, %(artists)s, %(album)s, %(is_explicit)s, %(duration_ms)s, %(spotify_trackID)s, %(apple_trackID)s, %(bpm)s, %(is_cover)s, %(has_lyrics)s, %(courtesy_of)s, %(lyric_file)s)")
            data = (track_name, artists, album, is_explicit, duration_ms, spotify_trackID,
                    apple_trackID, is_cover, has_lyrics, courtesy_of, lyric_file)
            self.cursor.execute(insertRow, data)
            assert(commitToDB())
            return True
        except:
            print(traceback.format_exc())
            return False

    def commitToDB(self):
        try:
            self.lySQL.commit()
            return True
        except:
            print(traceback.format_exc())
            return False
