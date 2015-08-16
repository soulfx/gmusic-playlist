# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

import re
import datetime
import math
import time
from common import *

# the file for outputing the information google has one each song
csvfile = None

# cleans up any open resources
def cleanup():
    if csvfile:
        csvfile.close()
    close_log()
    close_api()

# compares two strings based only on their characters
def s_in_s(string1,string2):
    if not string1 or not string2:
        return False
    s1 = re.compile('[\W_]+', re.UNICODE).sub(u'',string1.lower())
    s2 = re.compile('[\W_]+', re.UNICODE).sub(u'',string2.lower())

    return s1 in s2 or s2 in s1

# sleeps a little bit after printing message before exiting
def delayed_exit(message):
    log(message)
    time.sleep(5)
    cleanup()
    exit()

# add the song
def add_song(details,score):
    (result_score,score_reason) = score

    if ('+' in result_score and log_high_matches) or '-' in result_score:
        log(result_score+track+score_reason+u' #'+str(len(song_ids)))
        log (u'   ' + create_details_string(details, True))

    if not allow_duplicates and details['songid'] in song_ids:
        return

    song_ids.append(details['songid'])
    csvfile.write(create_details_string(details))
    csvfile.write(os.linesep)

# log an unmatched track
def log_unmatched(track):
    global no_matches
    log(u'!! '+track)
    csvfile.write(track)
    csvfile.write(os.linesep)
    no_matches += 1

# search for the song with the given details
def search_for_track(details):
    search_results = []
    dlog('search details: '+str(details))

    # search the personal library for the track
    lib_album_match = False
    if details['artist'] and details['title'] and search_personal_library:
        lib_results = [item for item in library if
            s_in_s(details['artist'],item.get('artist'))
            and s_in_s(details['title'],item.get('title'))]
        dlog('lib search results: '+str(len(lib_results)))
        for result in lib_results:
            if s_in_s(result['album'],details['album']):
                lib_album_match = True
            item = {}
            item[u'track'] = result
            item[u'score'] = 200
            search_results.append(item)

    # search all access for the track
    if not lib_album_match:
        query = u''
        if details['artist']:
            query = details['artist']
        if details['title']:
            query += u' ' + details['title']
        if not len(query):
            query = track
        dlog('aa search query:'+query)
        aa_results = api.search_all_access(query,max_results=7).get(
            'song_hits')
        dlog('aa search results: '+str(len(aa_results)))
        search_results.extend(aa_results)

    if not len(search_results):
        return None

    top_result = search_results[0]
    # if we have detailed info, perform a detailed search
    if details['artist'] and details['title']:
        search_results = [item for item in search_results if
            s_in_s(details['title'],item['track']['title'])
            and s_in_s(details['artist'],item['track']['artist'])]
        if details['album']:
            search_results = [item for item in search_results if
                    s_in_s(details['album'],item['track']['album'])]
        dlog('detail search results: '+str(len(search_results)))
        if len(search_results) != 0:
            top_result = search_results[0]

    return top_result

# match score stats
no_matches = 0
low_scores = 0
low_titles = 0
low_artists = 0
track_count = 0
duplicates = 0

# score the match against the query
def score_track(details,result_details,top_score = 200):
    global low_scores
    global low_titles
    global low_artists
    global duplicates

    # check for low quality matches
    result_score = u' + '
    score_reason = u' '
    is_low_result = False
    if top_score < 120:
        score_reason += u'{s}'
        #low scores alone don't seem to me a good indication of an issue
        #is_low_result = True
    # wrong song
    if ((details['title']
        and not s_in_s(details['title'],result_details['title']))
        or (not details['title']
        and not s_in_s(track,result_details['title']))):
        score_reason += u'{T}'
        low_titles += 1
        is_low_result = True
    # wrong album
    if (details['album'] and not ignore_album_mismatch
        and not s_in_s(details['album'],result_details['album'])):
        score_reason += u'{a}'
        is_low_result = True
    # wrong artist
    if (details['artist']
        and not s_in_s(details['artist'],result_details['artist'])):
        score_reason += u'{A}'
        low_artists += 1
        is_low_result = True
    # duplicate song
    if not allow_duplicates and result_details['songid'] in song_ids:
        score_reason += u'{D}'
        duplicates += 1
        is_low_result = True

    if is_low_result:
        result_score = u' - '
        low_scores += 1

    return (result_score,score_reason)

# check to make sure a filename was given
if len(sys.argv) < 2:
    delayed_exit(u'ERROR input filename is required')


# setup the input and output filenames and derive the playlist name
input_filename = sys.argv[1].decode('utf-8')
output_filename = os.path.splitext(input_filename)[0]
output_filename = re.compile('_\d{14}$').sub(u'',output_filename)
playlist_name = os.path.basename(output_filename)

output_filename += u'_' + unicode(datetime.datetime.now().strftime(
    '%Y%m%d%H%M%S'))
log_filename = output_filename + u'.log'
csv_filename = output_filename + u'.csv'

#open the log and output csv files
csvfile = codecs.open(csv_filename, encoding='utf-8', mode='w', buffering=1)
open_log(log_filename)

# read the playlist file into the tracks variable
tracks = []
plog('Reading playlist... ')
with codecs.open(input_filename, encoding='utf-8', mode='r', errors='ignore') as f:
    tracks = f.read().splitlines()
log('done. '+str(len(tracks))+' lines loaded.')

# log in and load personal library
api = open_api()
library = load_personal_library()

# begin searching for the tracks
log('===============================================================')
log(u'Searching for songs from: '+playlist_name)
log('===============================================================')


# gather up the song_ids and submit as a batch
song_ids = []

# collect some stats on the songs
stats = create_stats()

# time how long it takes
start_time = time.time()

# loop over the tracks that were read from the input file
for track in tracks:
    
    # skip empty lines
    if not track:
        continue

    # parse the track info if the line is in detail format
    details_list = get_csv_fields(track)
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
    if details['songid']:
        add_song(details,score_track(details,details))
        continue

    # search for the song
    search_result = search_for_track(details)

    # a details dictionary we can use for 'smart' searching
    smart_details = {}
    smart_details['title'] = details['title']
    smart_details['artist'] = details['artist']
    smart_details['album'] = details['album']

    if not details['title']:
        smart_details['title'] = track

    # if we didn't find anything strip out any (),{},[],<> from title
    match_string = '\[.*?\]|{.*?}|\(.*?\)|<.*?>'
    if not search_result and re.search(match_string,smart_details['title']):
        dlog('No results found, attempting search again with modified title.')
        smart_details['title'] = re.sub(match_string,'',smart_details['title'])
        search_result = search_for_track(smart_details)

    # if there isn't a result, try searching for the title only
    if not search_result and search_title_only:
        dlog('Attempting to search for title only')
        smart_details['artist'] = None
        smart_details['album'] = None
        smart_details['title_only_search'] = True
        search_result = search_for_track(smart_details)

    # check for a result
    if not search_result:
        log_unmatched(track)
        continue

    # gather up info about result
    result = search_result.get('track')
    result_details = create_result_details(result)
    result_score = score_track(details,result_details,
        search_result.get('score'))

    # if the song title doesn't match after a title only search, skip it
    (score,reason) = result_score
    if '{T}' in reason and 'title_only_search' in smart_details:
        log_unmatched(track)
        continue

    update_stats(result,stats)
    
    # add the song to the id list
    add_song(result_details,result_score)

total_time = time.time() - start_time

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
no_match_ratio = float(no_matches) / track_count if track_count else 0
low_score_ratio = float(low_scores) / track_count if track_count else 0
low_artists_ratio = float(low_artists) / low_scores if low_scores else 0
low_titles_ratio = float(low_titles) / low_scores if low_scores else 0
found_ratio = 1 - no_match_ratio - low_score_ratio

log('===============================================================')
log('   ' + str(len(song_ids)) + '/' + str(track_count) + ' tracks imported')
log(' ! ' + str(no_match_ratio*100) + '% of tracks could not be matched')
log(' - ' + str(low_score_ratio*100) + '% of tracks had low match scores')
log('  {T} ' + str(low_titles)
    + ' low matches were due to a song title mismatch')
log('  {A} ' + str(low_artists)
    + ' low matches were due to song artist mismatch')
if not allow_duplicates:
    log ('  {D} ' + str(duplicates)
        + ' duplicates were found and skipped')
log(' + ' + str(found_ratio*100) + '% of tracks had high match scores')
log('')
stats_results = calculate_stats_results(stats,len(song_ids))
log_stats(stats_results)

log('\nsearch time: '+str(total_time))

cleanup()

