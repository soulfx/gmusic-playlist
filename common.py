# Author: John Elkins <john.elkins@yahoo.com>
# License: MIT <LICENSE>

from collections import Counter
from gmusicapi import Mobileclient
from preferences import *
import time
import getpass

# create result details from the given track
def create_result_details(track):
    result_details = {}
    result_details['artist'] = track.get('artist')
    result_details['album'] = track.get('album')
    result_details['title'] = track.get('title')
    result_details['songid'] = (track.get('storeId')
        if track.get('storeId') else track.get('id'))
    return result_details

# create details dictionary based off the given details list
def create_details(details_list):
    details = {}
    details['artist'] = None
    details['album'] = None
    details['title'] = None
    details['songid'] = None
    if len(details_list) < 2:
        return details
    for pos, nfo in enumerate(details_list):
        details[track_info_order[pos]] = nfo.strip()
    return details

# create details string based off the given details dictionary
def create_details_string(details_dict, skip_id = False):
    out_string = u''
    for nfo in track_info_order:
        if skip_id and nfo == 'songid':
            continue
        if len(out_string) != 0:
            out_string += track_info_separator
        out_string += details_dict[nfo]
    return out_string

# log into google music
def login():
    # get the password each time so that it isn't stored in plain text
    password = getpass.getpass(username + '\'s password: ')
    
    api = Mobileclient()
    if not api.login(username, password):
        print 'ERROR unable to login'
        time.sleep(3)
        exit()
        
    password = None

    return api

# create a stats dictionary
def create_stats():
    stats = {}
    stats['genres'] = []
    stats['artists'] = []
    stats['years'] = []
    stats['total_playcount'] = 0
    return stats

# update the stats dictionary with info from the track
def update_stats(track,stats):
    stats['artists'].append(track.get('artist'))
    if track.get('genre'): stats['genres'].append(track.get('genre'))
    if track.get('year'): stats['years'].append(track.get('year'))
    if track.get('playCount'): stats['total_playcount'] += track.get(
        'playCount')

# calculate stats
def calculate_stats_results(stats,total_tracks):
    results = {}
    results['genres'] = Counter(stats['genres'])
    results['artists'] = Counter(stats['artists'])
    results['years'] = Counter(stats['years'])
    results['playback_ratio'] = stats['total_playcount']/float(total_tracks)
    return results    

# log the results
def log_stats(log,results):
    log(u'top 3 genres: '+repr(results['genres'].most_common(3)))
    log(u'top 3 artists: '+repr(results['artists'].most_common(3)))
    log(u'top 3 years: '+repr(results['years'].most_common(3)))
    log(u'playlist playback ratio: '+unicode(results['playback_ratio']))
