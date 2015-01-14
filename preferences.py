
# the username to use
username = 'john.elkins@gmail.com'

# the separator to use for detailed track information
track_info_separator = u'\\'
#track_info_separator = u'|'

# the order of the track details
track_info_order = ['title','artist','album','songid']
#track_info_order = ['title','artist','album','genre','year','durationMillis','playCount','rating','songid']

# output debug information to the log
debug = False

# don't import or export the same song twice
allow_duplicates = False

# == ImportList.py preferences ==============================================

# ignore mismatched albums.  An album mismatch often doesn't mean the song is
# wrong.  This is set to true so that mismatched albums don't scew the results
# and flag too many songs with low scores
ignore_album_mismatch = True

# search for tracks in the personal library, tracks found there will work
# for you, but if you share your playlist others may not be able to play
# some tracks.  Set to false if you want to make sure that your playlist doesn't
# contain any tracks that are not shareable.
search_personal_library = True

# when unable to locate a track using full details (title,artist,album); perform
# a search using only the song title.  this will hopefully find something to
# at least put into the track spot.  this is handy for playlists that list the
# composer or songwriter for a song instead of a singer.
search_title_only = True

# log high matches in addition to the songs that couldn't be found or had
# low matches.
log_high_matches = False
