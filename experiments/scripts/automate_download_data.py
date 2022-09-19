# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
from datetime import datetime
import pathlib

import googleapiclient.discovery
import googleapiclient.errors

import json

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    api_key_path = "../api_key.txt"
    output_path = "../data/"

    # API information
    api_service_name = "youtube"
    api_version = "v3"

    # Extract the api without having to hard code it
    with open(api_key_path, "r") as api_file:
        api_key = api_file.read()

    # Create the youtube client with api_key (API_KEY)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)

    request = youtube.videos().list(
        part="id,snippet,contentDetails,status,statistics,player,topicDetails,recordingDetails,liveStreamingDetails,localizations",
        chart="mostPopular",
        maxResults=50,
        regionCode="US",
        prettyPrint=True
    )
    response = request.execute()
    time = datetime.now()
    time_str = time.strftime("%m-%d-%Y_%H-%M-%S")
    for item in response["items"]:
        item["queryTime"] = time_str
        item["queryTimestamp"] = time.timestamp()


    with open(output_path + f"{time_str}_output.json", "w") as outfile:
        json.dump(response, outfile, indent = 4)

if __name__ == "__main__":
    main()
