# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

import re
import datetime
import sys
import os
import codecs
import math
from common import *

# search for tracks in the personal library, tracks found there will work
# for you, but if you share your playlist others may not be able to play
# some tracks
search_personal_library = True

# check to make sure a filename was given
if len(sys.argv) != 2:
    print 'ERROR input filename is required'
    time.sleep(3)
    exit()

# log in
api = login()

# setup the input and output filenames and derive the playlist name
input_filename = sys.argv[1].decode('utf-8')
output_filename = os.path.splitext(input_filename)[0]
output_filename = re.compile('_\d{14}$').sub(u'',output_filename)
playlist_name = os.path.basename(output_filename)

output_filename += u'_' + unicode(datetime.datetime.now().strftime(
    '%Y%m%d%H%M%S'))
log_filename = output_filename + u'.log'
tsv_filename = output_filename + u'.tsv'

# open the files
with codecs.open(input_filename, encoding='utf-8', mode='r') as f:
    tracks = f.read().splitlines()
logfile = codecs.open(log_filename, encoding='utf-8', mode='w', buffering=1)
tsvfile = codecs.open(tsv_filename, encoding='utf-8', mode='w', buffering=1)

# log to both the console and log file
def log(message):
    print message.encode(sys.stdout.encoding, errors='replace')
    logfile.write(message)
    logfile.write(os.linesep)

# log search results to the log and to the tsv
def log_search_results(artist,album,title,song_id):
    # log the match results    
    log (u'   ' + artist + u' - ' + album + u' - ' + title )

    # add the found song to the tsv file
    tsvfile.write(artist + u'\t' + album + u'\t' + title + u'\t' + song_id )
    tsvfile.write(os.linesep)

log('Loading library')
library = api.get_all_songs()

# begin searching for the tracks
log('===============================================================')
log(u'Searching for songs from: '+playlist_name)
log('===============================================================')

# keep track of stats
no_matches = 0
low_scores = 0
track_count = 0

# gather up the song_ids and submit as a batch
song_ids = []

# collect some stats on the songs
stats = create_stats()

# loop over the tracks that were read from the input file
for track in tracks:
    
    # skip empty lines
    if not track:
        continue

    # parse the track info if the line is in tsv format
    track_fields = track.split(u'\t')
    track_artist = None
    track_album = None
    track_title = None
    track_id = None

    if len(track_fields) == 2:
        # skip this, but treat it as a comment
        log(track_fields[1])
        # write it safely into the tsv file
        tsvfile.write(u'\t')
        tsvfile.write(re.compile('\t').sub(u' - ',track_fields[1]))
        tsvfile.write(os.linesep)
        continue
    if len(track_fields) >= 3:
        track_artist = track_fields[0]
        track_album = track_fields[1]
        track_title = track_fields[2]
        if not track_artist and not track_album and not track_title:
            # empty record
            continue
    if len(track_fields) >= 4:
        track_id = track_fields[3]

    # at this point we should have a valid track
    track_count += 1

    # don't search if we already have a track id
    if track_id and use_track_ids:
        song_ids.append(track_id)
        log_search_results(track_artist,track_album,track_title,track_id)
        continue

    # search for the track
    search_results = []

    # search the personal library for the track
    if track_artist and track_title and search_personal_library:
        search_results = [item for item in library if track_artist.lower()
            in item.get('artist').lower() and track_title.lower()
            in item.get('title').lower()]
        if len(search_results) != 0:
            result_data = {}
            result_data[u'track'] = search_results[0]
            result_data[u'score'] = 200
            search_results = [result_data]

    # search all access for the track
    if len(search_results) == 0:
        query = track
        if track_album:
            query = track_artist + u' ' + track_title
        search_results = api.search_all_access(query,max_results=7).get(
            'song_hits')

    # check for a result
    if len(search_results) == 0:
        log(u'!! '+track)
        tsvfile.write(track)
        tsvfile.write(os.linesep)
        no_matches += 1
        continue

    top_result = search_results[0]
    # if we have tsv info, perform a detailed search
    if track_artist and track_title and track_album:
        search_results = [item for item in search_results if track_title.lower()
	    in item['track']['title'].lower() and track_artist.lower()
            in item['track']['artist'].lower() and track_album.lower()
            in item['track']['album'].lower()]
        if len(search_results) != 0:
            top_result = search_results[0]

    # gather up info about result
    song = top_result.get('track')
    song_id = song.get('storeId') if song.get('storeId') else song.get('id')
    song_title = song.get('title')
    song_artist = song.get('artist')
    song_album = song.get('album')
    update_stats(song,stats)

    # check for low quality matches
    result_score = u' + '
    is_low_result = False
    if top_result.get('score') < 120:
        is_low_result = True
    # wrong song
    if not song_title.lower() in track.lower():
        is_low_result = True
    # wrong album
    if track_album and track_album.lower() not in song_album.lower():
        is_low_result = True
    # wrong artist
    if track_artist and track_artist.lower() not in song_artist.lower():
        is_low_result = True
        
    if is_low_result:
        result_score = u' - '
        low_scores += 1

    # display the original track for reference
    log(result_score+track)

    log_search_results(song_artist,song_album,song_title,song_id)
    
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

    added_songs = api.add_songs_to_playlist(playlist_id,current_songs)

    log(u' + '+current_playlist_name+u' - '+unicode(len(added_songs))+
        u'/'+unicode(len(current_songs))+' songs')

    # go to the next playlist section
    current_playlist += 1

# log a final status
no_match_ratio = float(no_matches) / track_count
low_score_ratio = float(low_scores) / track_count
found_ratio = 1 - no_match_ratio - low_score_ratio

log('===============================================================')
log('   ' + str(len(song_ids)) + '/' + str(track_count) + ' tracks imported')
log(' ! ' + str(no_match_ratio) + ' percent of tracks could not be matched')
log(' - ' + str(low_score_ratio) + ' percent of tracks had low match scores')
log(' + ' + str(found_ratio) + ' percent of tracks had high match scores')
log('')
stats_results = calculate_stats_results(stats,len(song_ids))
log_stats(log,stats_results)

logfile.close()
tsvfile.close()
api.logout()

