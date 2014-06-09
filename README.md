gmusic-playlist
===============

playlist scripts for gmusic

## Prerequisites

python 2.7 - https://www.python.org

gmusicapi - https://github.com/simon-weber/Unofficial-Google-Music-API

Before using the scripts, open up the common.py file and change the username.

When the scripts are run they will prompt for your password.  If you use two factor authentication you will need to create and use an application password.

## ExportLists.py

This script will export all playlists to a given directory as tsv files.  Tsv files are like csv files, but use tabs to seperate each field.  Most spreadsheet apps can open this type of file.  If you edit the file in a text editor remember to use tabs.

The format of each track is: artistTalbumTtitleTsongId  where T is the tab character.

The tsv files can be re-imported using the ImportList.py script.

Command Line Usage: python ExportLists.py OutputDir

GUI Usage (Windows): Drag and drop OutputDir onto ExpertLists.py

OutputDir is a directory you would like the playlists to be output to.

The export progress will be output to the console and to a log file.  At the completion of the export a status of the overal makeup of the playlist will be output.

## ImportList.py

This script will import a given text file into google music as a playlist. The title of the playlist will be the name of the text file and each track will be matched to each line in the text file.

Command Line Usage: python ImportList.py ExamplePlaylist.txt

GUI Usage (Windows): Drag and Drop the ExamplePlaylist.txt file onto ImportList.py

The progress of the playlist creation will be output to the console and to a log file.  Tracks that could not be found are prefixed with !! and tracks that were found but may not be a good match are prefixed with -.  In addition to a log file, a tsv file is created which contains all tracks found and their associated google music song id.

The tsv file output from the ImportList.py script can be used to fix any song that didn't import correctly.  Open the tsv file, look for the songs without any song id and see if there is something that you can change in the track info to get google to find the song.  Save the file and then re-run it through the ImportList.py script.  Since the TSV file will contain the song id's for songs it already found it won't need to look those up again and will just focus on finding the songs that don't have id's yet.

## Playlist files

The format of each track in a playlist file can either be fuzzy or detailed info.  Comments are also supported.

A fuzzy track is a track that has no tabs and simply lists a song title, song title and author, or song author and title.  See the ExamplePlaylist.txt file for a few examples of fuzzy tracks.  Fuzzy tracks will only be matched to all access tracks.  If you have a song in a playlist that isn't in all access, but is in your personal library you will need to use a detailed track.

A detailed track lists song information using tsv format.  A tsv formatted track consists of artistTalbumTtitleTsongId where T is the tab character.  The songId is optional, and will be added by the scripts when outputting a tsv file.  See the ExamplePlaylist.txt file for a few examples of detailed track lists.  The album can be left out if not required: ie the track listing would be formatted like artistTTtitle.

A comment in a playlist file follows the form of Tcomment where T is the tab character and comment is the comment.  See the ExamplePlaylist.txt file.
