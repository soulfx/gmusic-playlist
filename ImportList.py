# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

import re
import datetime
import sys
import os
import codecs
import math
from common import *

tsep = track_info_separator

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
csv_filename = output_filename + u'.csv'

# open the files
with codecs.open(input_filename, encoding='utf-8', mode='r') as f:
    tracks = f.read().splitlines()
logfile = codecs.open(log_filename, encoding='utf-8', mode='w', buffering=1)
csvfile = codecs.open(csv_filename, encoding='utf-8', mode='w', buffering=1)

# log to both the console and log file
def log(message, proceed = True):
    if not proceed:
        return
    print message.encode(sys.stdout.encoding, errors='replace')
    logfile.write(message)
    logfile.write(os.linesep)

# log search results to the log and to the csv
def log_search_results(details):
    # log the match results    
    log (u'   ' + create_details_string(details, True))

    # add the found song to the csv file
    csvfile.write(create_details_string(details))
    csvfile.write(os.linesep)

# compare two strings based only on their characters
def s_in_s(string1,string2,start=u''):
    if not string1 or not string2:
        return False
    s1 = re.compile('[\W_]+', re.UNICODE).sub(u'',string1.lower())
    s2 = re.compile('[\W_]+', re.UNICODE).sub(u'',string2.lower())
    return re.search(start+s1,s2) or re.search(start+s2,s1)

log('Loading library')
library = api.get_all_songs()

# begin searching for the tracks
log('===============================================================')
log(u'Searching for songs from: '+playlist_name)
log('===============================================================')

# keep track of stats
no_matches = 0
low_scores = 0
low_titles = 0
low_artists = 0
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

    # parse the track info if the line is in detail format
    details_list = track.split(tsep)
    details = create_details(details_list)

    # skip comment lines
    if len(details_list) == 2 and not details_list[0]:
        log(details_list[1])
        csvfile.write(tsep)
        csvfile.write(details_list[1])
        csvfile.write(os.linesep)
        continue

    # skip empty details records
    if (len(details_list) >= 3 and not details['artist']
        and not details['album'] and not details['title']):
        continue

    # at this point we should have a valid track
    track_count += 1

    # don't search if we already have a track id
    if details['songid'] and use_track_ids:
        song_ids.append(details['songid'])
        log_search_results(details)
        continue

    # search for the track
    search_results = []

    # search the personal library for the track
    lib_album_match = False
    if details['artist'] and details['title'] and search_personal_library:
        lib_results = [item for item in library if
            s_in_s(details['artist'],item.get('artist'))
            and s_in_s(details['title'],item.get('title'))]
        log('lib search results: '+str(len(lib_results)),debug)
        for result in lib_results:
            if s_in_s(result['album'],details['album']):
                lib_album_match = True
            item = {}
            item[u'track'] = result
            item[u'score'] = 200
            search_results.append(item)

    # search all access for the track
    if not lib_album_match:
        query = track
        if details['artist'] and details['title']:
            query = details['artist'] + u' ' + details['title']
        aa_results = api.search_all_access(query,max_results=7).get(
            'song_hits')
        log('aa search results: '+str(len(aa_results)),debug)
        search_results.extend(aa_results)

    # check for a result
    if len(search_results) == 0:
        log(u'!! '+track)
        csvfile.write(track)
        csvfile.write(os.linesep)
        no_matches += 1
        continue

    top_result = search_results[0]
    # if we have detailed info, perform a detailed search
    if details['artist'] and details['title'] and details['album']:
        search_results = [item for item in search_results if
            s_in_s(details['title'],item['track']['title'])
            and s_in_s(details['artist'],item['track']['artist'])
            and s_in_s(details['album'],item['track']['album'])]
        log('detail search results: '+str(len(search_results)),debug)
        if len(search_results) != 0:
            top_result = search_results[0]

    # gather up info about result
    result = top_result.get('track')
    result_details = create_result_details(result)

    update_stats(result,stats)

    # check for low quality matches
    result_score = u' + '
    score_reason = u' '
    is_low_result = False
    if top_result.get('score') < 120:
        score_reason += u'{s}'
        is_low_result = True
    # wrong song
    if ((details['title']
        and not s_in_s(details['title'],result_details['title'],u'^'))
        or (not details['title']
        and not s_in_s(track,result_details['title']))):
        score_reason += u'{T}'
        low_titles += 1
        is_low_result = True
    # wrong album
    if (details['album'] and not ignore_album_mismatch
        and not s_in_s(details['album'],result_details['album'],u'^')):
        score_reason += u'{a}'
        is_low_result = True
    # wrong artist
    if (details['artist']
        and not s_in_s(details['artist'],result_details['artist'],u'^')):
        score_reason += u'{A}'
        low_artists += 1
        is_low_result = True

    if is_low_result:
        result_score = u' - '
        low_scores += 1

    # display the original track for reference
    log(result_score+track+score_reason)
    
    log_search_results(result_details)
    
    # add the song to the id list
    song_ids.append(result_details['songid'])

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
low_artists_ratio = float(low_artists) / low_scores
low_titles_ratio = float(low_titles) / low_scores
found_ratio = 1 - no_match_ratio - low_score_ratio

log('===============================================================')
log('   ' + str(len(song_ids)) + '/' + str(track_count) + ' tracks imported')
log(' ! ' + str(no_match_ratio) + ' percent of tracks could not be matched')
log(' - ' + str(low_score_ratio) + ' percent of tracks had low match scores')
log('  {T} ' + str(low_titles)
    + ' low matches were due to a song title mismatch')
log('  {A} ' + str(low_artists)
    + ' low matches were due to song artist mismatch')
log(' + ' + str(found_ratio) + ' percent of tracks had high match scores')
log('')
stats_results = calculate_stats_results(stats,len(song_ids))
log_stats(log,stats_results)

logfile.close()
csvfile.close()
api.logout()

