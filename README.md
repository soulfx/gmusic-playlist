gmusic-playlist
===============

playlist scripts for gmusic

Prerequisites

python - https://www.python.org
gmusicapi - https://github.com/simon-weber/Unofficial-Google-Music-API

ImportList.py

This script will import a given text file into google music as a playlist. The title of the playlist will be the name of the text file and each track will be matched to each line in the text file.

Before using the ImportList.py script open it up and change the username.

Command Line Usage: python ImportList.py ExamplePlaylist.txt

GUI Usage (Windows): Drag and Drop the ExamplePlaylist.txt file onto ImportList.py

When the program is run it will prompt for your password.  If you use two factor authentication you will need to create an application password.

The progress of the playlist creation will be output to the console and to a log file.  Tracks that could not be found are prefixed with ! and tracks that were found but may not be a good match are prefixed with -.
