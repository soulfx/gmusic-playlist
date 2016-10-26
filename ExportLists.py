# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

from common import *

if len(sys.argv) < 2:
    log('ERROR output directory is required')
    time.sleep(3)
    exit()

# setup the output directory, create it if needed
output_dir = sys.argv[1]
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# log in and load personal library
api = open_api()
library = load_personal_library()

def playlist_handler(playlist_name, playlist_description, playlist_tracks):
    # skip empty and no-name playlists
    if not playlist_name: return
    if len(playlist_tracks) == 0: return

    # setup output files
    playlist_name = playlist_name.replace('/', '')
    open_log(os.path.join(output_dir,playlist_name+u'.log'))
    outfile = codecs.open(os.path.join(output_dir,playlist_name+u'.csv'),
        encoding='utf-8',mode='w')

    # keep track of stats
    stats = create_stats()
    export_skipped = 0
    # keep track of songids incase we need to skip duplicates
    song_ids = []

    log('')
    log('============================================================')
    log(u'Exporting '+ unicode(len(playlist_tracks)) +u' tracks from '
        +playlist_name)
    log('============================================================')

    # add the playlist description as a "comment"
    if playlist_description:
        outfile.write(tsep)
        outfile.write(playlist_description)
        outfile.write(os.linesep)

    for tnum, pl_track in enumerate(playlist_tracks):
        track = pl_track.get('track')

        # we need to look up these track in the library
        if not track:
            library_track = [
                item for item in library if item.get('id')
                in pl_track.get('trackId')]
            if len(library_track) == 0:
                log(u'!! '+str(tnum+1)+repr(pl_track))
                export_skipped += 1
                continue
            track = library_track[0]

        result_details = create_result_details(track)

        if not allow_duplicates and result_details['songid'] in song_ids:
            log('{D} '+str(tnum+1)+'. '+create_details_string(result_details,True))
            export_skipped += 1
            continue

        # update the stats
        update_stats(track,stats)

        # export the track
        song_ids.append(result_details['songid'])
        outfile.write(create_details_string(result_details))
        outfile.write(os.linesep)

    # calculate the stats
    stats_results = calculate_stats_results(stats,len(playlist_tracks))

    # output the stats to the log
    log('')
    log_stats(stats_results)
    log(u'export skipped: '+unicode(export_skipped))

    # close the files
    close_log()
    outfile.close()

# the personal library is used so we can lookup tracks that fail to return
# info from the ...playlist_contents() call

playlist_contents = api.get_all_user_playlist_contents()

for playlist in playlist_contents:
    playlist_name = playlist.get('name')
    playlist_description = playlist.get('description')
    playlist_tracks = playlist.get('tracks')

    playlist_handler(playlist_name, playlist_description, playlist_tracks)

if export_thumbs_up:
    # get thumbs up playlist
    thumbs_up_tracks = []
    for track in library:
        if track.get('rating') is not None and int(track.get('rating')) > 1:
            thumbs_up_tracks.append(track)


    # modify format of each dictionary to match the data type
    # of the other playlists
    thumbs_up_tracks_formatted = []
    for t in thumbs_up_tracks:
        thumbs_up_tracks_formatted.append({'track': t})

    playlist_handler('Thumbs up', 'Thumbs up tracks', thumbs_up_tracks_formatted)

if export_all:
    all_tracks_formatted = []
    for t in library:
        all_tracks_formatted.append({'track': t})

    playlist_handler('All', 'All tracks', all_tracks_formatted)

close_api()
    
