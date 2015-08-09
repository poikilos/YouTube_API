#!/usr/bin/python

import httplib2
import os
import sys
import json

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "auth.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=YOUTUBE_READ_WRITE_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
  http=credentials.authorize(httplib2.Http()))

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.
channels_response = youtube.channels().list(
  mine=True,
  part="contentDetails"
).execute()


uploads_list_id = list("PL3NszaL-ztEDs89mEbqx6UoSBa9ezi4r9")

def loop_list(playlistId):
  video_urls = []
  page = 1

  while page<3:
    if page==1:
        playlistitems_list_request = youtube.playlistItems().list(
          playlistId=playlistId,
          part="snippet,contentDetails",
          maxResults=50
        ).execute()

        for playlist_item in playlistitems_list_request["items"]:
          video_id = playlist_item["snippet"]["resourceId"]["videoId"]
          video_urls.append("https://www.youtube.com/watch?v=%s" % video_id)
        
        nextpage = playlistitems_list_request["nextPageToken"]

    elif page==4:
        playlistitems_list_request = youtube.playlistItems().list(
          playlistId=playlistId,
          part="snippet,contentDetails",
          maxResults=50,
          pageToken=nextpage
        ).execute()

        for playlist_item in playlistitems_list_request["items"]:
          video_id = playlist_item["snippet"]["resourceId"]["videoId"]
          video_urls.append("https://www.youtube.com/watch?v=%s" % video_id)

    else:
        playlistitems_list_request = youtube.playlistItems().list(
          playlistId=playlistId,
          part="snippet,contentDetails",
          maxResults=50,
          pageToken=nextpage
        ).execute()

        for playlist_item in playlistitems_list_request["items"]:
          video_id = playlist_item["snippet"]["resourceId"]["videoId"]
          video_urls.append("https://www.youtube.com/watch?v=%s" % video_id)

        nextpage = playlistitems_list_request["nextPageToken"]
    page+=1

  return video_urls

URls = []

def get_playlist(playlistIds):
  for key, value in playlistIds.iteritems():
      count = 1
      for x in loop_list(value):
        URls.append((x,key))
        count+=1

playlistIds = {
  # "Music 0": "PL3NszaL-ztEAcB2ZkPjM-O2zylniVlk2Q",
  "Music 1": "PL143007D86913057E",
  "Music 2": "PLB2C4F408EDCA77D9",
  "Music 3": "PL23BA0FA321510EB0",
  "Music 4": "PL3NszaL-ztED6lkvfdJXriO3OFA6orwMt",
  "Music 5": "PL3NszaL-ztEBTHET_ttmm_Ij5A3Awzslv",
  "Music 6": "PL3NszaL-ztEDs89mEbqx6UoSBa9ezi4r9",
  }

get_playlist(playlistIds)


f = open('urls','w')

for x in URls:
  f.write('%s,%s \n' % (x[1],x[0])) # python will convert \n to os.linesep

f.close() # you can omit in most cases as the destructor will call it