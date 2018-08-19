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

# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import datetime

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#     https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#     https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

     {}

with information from the Developers Console
https://console.developers.google.com/
(If you have finished the setup instructions
but do not have a "OAuth 2.0 client IDs" section listed there,
you must click "Create Credentials," "OAuth ID")

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""".format(os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        CLIENT_SECRETS_FILE)))

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account.
YOUTUBE_READ_WRITE_SCOPE = "https://www.googleapis.com/auth/youtube"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

flow = flow_from_clientsecrets(
    CLIENT_SECRETS_FILE,
    message=MISSING_CLIENT_SECRETS_MESSAGE,
    scope=YOUTUBE_READ_WRITE_SCOPE
)

storage = Storage("{}-oauth2.json".format(sys.argv[0]))
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


def to_csv_field(s):
    if s is None:
        s = ""
    elif (',' in s) or ('"' in s):
        s = s.replace('"', '""')
        s = '"' + s + '"'
    return s


def loop_list(playlistId, key):
    video_urls = []
    page = 1
    nextpage = True
    entry_n = 1
    while nextpage is not None:
        if page == 1:
            playlistitems_list_request = youtube.playlistItems().list(
                playlistId=playlistId,
                part="snippet,contentDetails",
                maxResults=50
            ).execute()
        else:
            playlistitems_list_request = youtube.playlistItems().list(
                playlistId=playlistId,
                part="snippet,contentDetails",
                maxResults=50,
                pageToken=nextpage
            ).execute()
        for item in playlistitems_list_request["items"]:
            video_id = item["snippet"]["resourceId"]["videoId"]
            try:
                video_name = unicode(item["snippet"]["title"]).encode(
                    'ascii', 'replace').replace(",", "")
            except NameError:
                # Python 3 (unicode replaced by str, str by bytes)
                video_name = str(item["snippet"]["title"]).replace(
                                 ",", "")
            video_urls.append("https://www.youtube.com/watch?v=" +
                              to_csv_field(video_id) + "," +
                              to_csv_field(key) + ", " +
                              to_csv_field(video_name))
            print(str(entry_n) + ". " + video_name)
            entry_n += 1

        nextpage = playlistitems_list_request.get("nextPageToken")
        page += 1

    return video_urls

csvLines = []


def get_playlist(playlistIds):
    print("")
    for key, value in playlistIds.items():
        count = 1
        print("")
        print("## " + key + ":")
        for x in loop_list(value, key):
            csvLines.append(x)
            count += 1

playlistIds = {}

digits = "01234567890"
float_chars = "01234567890."


def is_int_like(s):
    ret = False
    if s is not None:
        ret = True
        for c in s:
            if c not in digits:
                ret = False
                break
    return ret


def is_float_like(s):
    ret = False
    if s is not None:
        ret = True
        for c in s:
            if c not in float_chars:
                ret = False
                break
    return ret


def decodeYamlField(s):
    ret = None
    s_strip = s.strip()
    if (s_strip != "~") and (s_strip != "null"):
        if ((len(s_strip) > 1) and (s_strip[0] == '"') and
                (s_strip[-1] == '"')):
            ret = s_strip[1:-1].replace("\\n", "\n")
        elif ((len(s_strip) > 1) and (s_strip[0] == "'") and
                (s_strip[-1] == '"')):
            ret = s_strip[1:-1]
        else:
            if is_int_like(s_strip):
                ret = int(s_strip)
            elif is_float_like(s_strip):
                ret = float(s_strip)
            else:
                ret = s_strip
    return ret


def decodeYamlStr(s):
    ret = None
    s_strip = ""
    if s is not None:
        s_strip = s.strip()
        if (s_strip != "~") and (s_strip != "null"):
            if ((len(s_strip) > 1) and (s_strip[0] == '"') and
                    (s_strip[-1] == '"')):
                ret = s_strip[1:-1].replace("\\n", "\n")
            elif ((len(s_strip) > 1) and (s_strip[0] == "'") and
                    (s_strip[-1] == '"')):
                ret = s_strip[1:-1]
            else:
                ret = s_strip
    return ret

playlists_path = "playlists.yml"
if os.path.isfile(playlists_path):
    ins = open(playlists_path)
    line = True
    line_n = 1
    while line:
        line = ins.readline()
        if line:
            line = line.rstrip()  # remove newline character
            sign_i = line.find(":")
            if sign_i > 0:
                playlistName = decodeYamlStr(line[:sign_i].strip())
                playlistId = decodeYamlStr(line[sign_i+1:].strip())
                if len(playlistName) > 0:
                    if len(playlistId) > 0:
                        playlistIds[playlistName] = playlistId
                    else:
                        print(playlist_path + " (line " + str(line_n) +
                              "): input error: missing playlist id" +
                              " after ':'")
                else:
                    print(playlist_path + " (line " + str(line_n) +
                          "): input error: missing playlist name" +
                          " before ':'")
            else:
                print(playlist_path + " (line " + str(line_n) +
                      "): input error: missing ':' after playlist name")
        line_n += 1
    ins.close()
else:
    print("")
    print("You must have " + playlists_path +
          " with lines in the format:")
    print("Name: playlistID")
    print("")
    print("(the playlistID can be found in the address bar of your" +
          " browser when you are viewing the playlist)")
    print("")
    print("")
    sys.exit(1)

print("Using the following BesideTheVoid playlists:")
print(str(playlistIds))

get_playlist(playlistIds)

out_name = "urls_" + str(datetime.datetime.now()) + ".csv"
data_path = "YouTubePlaylists"
out_path = os.path.join(data_path, out_name)
if not os.path.isdir(data_path):
    os.makedirs(data_path)
# print("#Writing '" + out_path + "...")
f = open(out_path, 'w')

for x in csvLines:
    f.write(x + '\n')    # python will convert \n to os.linesep

f.close()
print("#finished writing " + os.path.abspath(out_path))
