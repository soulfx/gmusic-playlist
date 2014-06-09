# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

import os
import sys
import codecs
from common import *


if len(sys.argv) != 2:
    print 'ERROR output directory is required'
    time.sleep(3)
    exit()

output_dir = sys.argv[1]

# log in
api = login()

# load the library so we can lookup tracks that fail to return
# info vai the ...playlist_contents() call
print 'Loading Library'
library = api.get_all_songs()
playlist_contents = api.get_all_user_playlist_contents()

for playlist in playlist_contents:
    playlist_name = playlist.get('name')
    playlist_description = playlist.get('description')
    playlist_tracks = playlist.get('tracks')
    
    # skip empty and no-name playlists
    if not playlist_name: continue
    if len(playlist_tracks) == 0: continue

    # setup output files
    logfile = open(os.path.join(output_dir,playlist_name+u'.log'),'w',1)
    outfile = codecs.open(os.path.join(output_dir,playlist_name+u'.tsv'),
        encoding='utf-8',mode='w')
    def log(message):
        print message
        logfile.write(message)
        logfile.write(os.linesep)

    # keep track of stats
    stats = create_stats()
    export_skipped = 0

    log('============================================================')
    log(u'Exporting '+ unicode(len(playlist_tracks)) +u' tracks from '
        +playlist_name)
    log('============================================================')

    # add the playlist description as a "comment"
    if playlist_description:
        outfile.write(u'\t')
        outfile.write(playlist_description)
        outfile.write(os.linesep)
    
    for pl_track in playlist_tracks:

        track = pl_track.get('track')

        # we need to look up these track in the library
        if not track:
            library_track = [item for item in library if item.get('id')
                in pl_track.get('trackId')]
            if len(library_track) == 0:
                log(u'unable to load information for: '+repr(pl_track))
                export_skipped += 1
                continue
            track = library_track[0]

        track_artist = track.get('artist')
        track_album = track.get('album')
        track_title = track.get('title')
        track_id = track.get('storeId') if track.get('storeId') else track.get(
            'id')

        # update the stats
        update_stats(track,stats)

        # export the track
        outfile.write(track_artist + u'\t' + track_album + u'\t' + track_title)
        if use_track_ids:
            outfile.write(u'\t' + track_id)
        outfile.write(os.linesep)

    # calculate the stats
    stats_results = calculate_stats_results(stats,len(playlist_tracks))

    # output the stats to the log
    log_stats(log,stats_results)
    log(u'export skipped: '+unicode(export_skipped))

    # close the files
    logfile.close()
    outfile.close()

api.logout()
    
