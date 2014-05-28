# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <see _MIT_License.txt>

import getpass
import sys
import os
import codecs
from gmusicapi import Mobileclient

# the username to use
username = 'john.elkins@gmail.com'

if len(sys.argv) != 2:
    print 'ERROR filename is required'
    exit()

# try to support utf-8 playlist and track names
filepath = sys.argv[1].decode('utf-8')
logpath = os.path.splitext(filepath)[0]+u'.log'
with codecs.open(filepath, encoding='utf-8', mode='r') as f:
    tracks = f.read().splitlines()
logfile = codecs.open(logpath, encoding='utf-8', mode='w', buffering=1)

# log to both the console and a text file
def log(message):
    print message.encode(sys.stdout.encoding, errors='replace')
    logfile.write(message)
    logfile.write(os.linesep)

# get the password each time so that it isn't stored in plain text
password = getpass.getpass(username + '\'s password: ')

# log in
api = Mobileclient()
logged_in = api.login(username, password)
password = None

if not logged_in:
    log('ERROR unable to login')
    exit()

# create the playlist
playlist_name = os.path.basename(os.path.splitext(filepath)[0])
log('===============================================================')
log(u'Creating Playlist: '+playlist_name)
log('===============================================================')
playlist_id = api.create_playlist(playlist_name)

# keep track of stats
no_matches = 0
low_scores = 0

# loop over the tracks
for track in tracks:
    # skip empty lines
    if not track:
        continue

    # search for the track
    top_result = api.search_all_access(track,max_results=1).get('song_hits')

    # TODO if the track isn't found in all access, then search the library
    # for the track since it may be part of my uploads

    # check for a result
    if len(top_result) == 0:
        log(u'!: '+track)
        no_matches += 1
        continue

    # check the result score
    top_result = top_result[0]
    result_score = u' + '
    if top_result.get('score') < 120:
        result_score = u' - '
        low_scores += 1

    # gather up info about result
    song = top_result.get('track')
    song_id = song.get('storeId')
    song_title = song.get('title')
    song_artist = song.get('artist')
    song_album = song.get('album')
    song_year = unicode(song.get('year'))

    log ( result_score + song_artist + u' - ' + song_title + u' - '
        + song_album + u' (' + song_year + u')' )
    
    # add the song to the playlist
    api.add_songs_to_playlist(playlist_id,song_id)

# log a final status
log('===============================================================')
log('Creation Complete: ' + str(no_matches) + '(!) no matches, '
    + str(low_scores) + '(-) low scores out of a total of '
    + str(len(tracks)) + ' tracks.' )

logfile.close()
api.logout()

