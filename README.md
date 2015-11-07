gmusic-playlist
===============

playlist scripts for gmusic

## Prerequisites

- python 2.7 - https://www.python.org
- gmusicapi - https://github.com/simon-weber/Unofficial-Google-Music-API
 - version >= https://github.com/simon-weber/gmusicapi/tree/d2a5cc91e209ec5fdf7ba89fe04d32c2a0155dff

Before using the scripts, open up the preferences.py file and change the username.

When the scripts are run they will prompt for your password.  If you use two factor authentication you will need to create and use an application password.

## ExportLists.py

This script will export all playlists to a given directory as csv files.  For the purpose of these scripts CSV stands for character seperated value.  The default separator charator is ','  The separator character is configurable in the preferences file.  Versions of the code previous to Aug 16 2015 used a '\' separator character as the default.  Most spreadsheet apps can open csv files.

The order in which the artist, album, and title information appears as well as the separating character between each piece of information is configured in the preference.py file.  The default order and separator character will output song info as: "title","artist","album","songid"

The csv files can be re-imported using the ImportList.py script.

Command Line Usage: python ExportLists.py OutputDir

OutputDir is a directory you would like the playlists to be output to.

The export progress will be output to the console and to a log file.  At the completion of the export a status of the overal makeup of the playlist will be output.

## ImportList.py

This script will import a given csv file into google music as a playlist. The title of the playlist will be the name of the text file and each track will be matched to each line in the text file.

Command Line Usage: python ImportList.py ExamplePlaylist.csv

The progress of the playlist creation will be output to the console and to a log file.  Tracks that could not be found are prefixed with !! and tracks that were found but may not be a good match are prefixed with -.  One or more of the following will appear after a track with a low match: {A}{a}{T}{s}  These markings indicate why the match was low,  {A} means the artist didn't match, {T} means the title didn't match, {a} means the album didn't match, and {s} means it had a low result score.  In addition to a log file, a csv file is created which contains all tracks found and their associated google music song id.

The csv file output from the ImportList.py script can be used to fix any song that didn't import correctly.  Open the csv file, look for the songs without any song id and see if there is something that you can change in the track info to get google to find the song.  Save the file and then re-run it through the ImportList.py script.  Since the csv file will contain the song id's for songs it already found it won't need to look those up again and will just focus on finding the songs that don't have id's yet.

You can also look up the song you want via google music's web interface and get the song id by clicking share > get link.  The song id is given in the link.

## Playlist files

The format of each track in a playlist file can either be fuzzy or detailed info.  Comments are also supported.

A fuzzy track is a track that has no separating characters and simply lists a song title, song title and author, or song author and title.  See the ExamplePlaylist.csv file for a few examples of fuzzy tracks.  Fuzzy tracks will only be matched to all access tracks.  If you have a song in a playlist that isn't in all access, but is in your personal library you will need to use a detailed track.

A detailed track lists title,artist,and album information separated by the separator character and in the order defined in the preferences.py file.  The songId is optional, and will be added by the scripts when outputting a csv file.  See the ExamplePlaylist.csv file for a few examples of detailed track lists.  The album can be left out if not required.

A comment in a playlist file follows the form of Ccomment where C is the separator character and comment is the comment.  See the ExamplePlaylist.csv file.
