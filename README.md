# YouTube_API

Interact with YouTube API in Python

## Primary Features
Download the URLs of all videos in any number of playlists into a CSV File

## Planned features
* download MP3 file from videos
* Automate conversion to MP3 file and downloading process
* Build Sync function to remove need to redownload already indexed music
* Automate fetching of music playlists

## Changes:
(2018-08-18)
(poikilos)
* Fix bug that prevents playlists with no next_page_token from downloading
* Convert data to CSV field before writing, so CSV format isn't corrupted
* Remove deprecated string formatting
