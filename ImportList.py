# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

import getpass
import sys
import os
import codecs
import math
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
log(u'Searching for ' +unicode(len(tracks))+ u' songs from: '+playlist_name)
log('===============================================================')

# keep track of stats
no_matches = 0
low_scores = 0

# gather up the song_ids and submit as a batch
song_ids = []

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
        log(u'!! '+track)
        no_matches += 1
        continue
    else:
        # display the original track for reference
        log(u'   '+track)

    top_result = top_result[0]

    # gather up info about result
    song = top_result.get('track')
    song_id = song.get('storeId')
    song_title = song.get('title')
    song_artist = song.get('artist')
    song_album = song.get('album')

    # check the result score
    result_score = u' + '
    if top_result.get('score') < 120:
        result_score = u' - '
        low_scores += 1
    # sometimes google picks a song that isn't what we want at all
    elif not song_title.lower() in track.lower():
        result_score = u' - '
        low_scores += 1
        
    log ( result_score + song_artist + u' - ' + song_title + u' - '
        + song_album )
    
    # add the song to the id list
    song_ids.append(song_id)

log('===============================================================')
log(u'Adding '+unicode(len(song_ids))+' found songs to: '+playlist_name)
log('===============================================================')

# add the songs to the playlist(s)
max_playlist_size = 1000
current_playlist = 1
total_playlists_needed = int(math.ceil(len(song_ids)/float(max_playlist_size)))
while current_playlist <= total_playlists_needed:
    # build the playlist name, add part number if needed
    current_playlist_name = playlist_name
    if total_playlists_needed > 1:
        current_playlist_name += u' Part ' + unicode(current_playlist)

    # create the playlist and add the songs
    playlist_id = api.create_playlist(current_playlist_name)
    current_playlist_index = ( current_playlist - 1 ) * max_playlist_size
    current_songs = song_ids[current_playlist_index :
                             current_playlist_index + max_playlist_size]
    api.add_songs_to_playlist(playlist_id,current_songs)

    log(u' + '+current_playlist_name+u' - '+unicode(len(current_songs))
        +' songs')

    # go to the next playlist section
    current_playlist += 1

# log a final status
no_match_ratio = float(no_matches) / len(tracks)
low_score_ratio = float(low_scores) / len(tracks)
found_ratio = 1 - no_match_ratio - low_score_ratio

log('===============================================================')
log('   ' + str(len(song_ids)) + '/' + str(len(tracks)) + ' tracks imported')
log(' ! ' + str(no_match_ratio) + ' percent of tracks could not be matched')
log(' - ' + str(low_score_ratio) + ' percent of tracks had low match scores')
log(' + ' + str(found_ratio) + ' percent of tracks had high match scores')

logfile.close()
api.logout()

