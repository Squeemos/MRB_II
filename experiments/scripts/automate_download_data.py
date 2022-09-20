# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
from datetime import datetime, timedelta
from pytz import timezone, UTC

import tinydb
from reader import YouTubeReader

import googleapiclient.discovery
import googleapiclient.errors

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
    api_key_path = "../../secret_keys/api_key.txt"
    output_path = "./database/"

    # API information
    api_service_name = "youtube"
    api_version = "v3"

    # Extract the api without having to hard code it
    with open(api_key_path, "r") as api_file:
        api_key = api_file.read()

    # # Create the youtube client with api_key (API_KEY)
    # youtube = googleapiclient.discovery.build(
    #     api_service_name, api_version, developerKey = api_key)
    #
    # request = youtube.videos().list(
    #     part="id,snippet,contentDetails,status,statistics,player,topicDetails,recordingDetails,liveStreamingDetails,localizations",
    #     chart="mostPopular",
    #     maxResults=50,
    #     regionCode="US"
    # )
    # response = request.execute()

    with tinydb.TinyDB(output_path + "youtube.json", indent = 2) as database:
        YtR = YouTubeReader()
        trending = database.table("TRENDING")
        # YtR.insert_videos(response, trending)

        thirty_days_ago = datetime.now(timezone("UTC")) - timedelta(days = 2)
        query = tinydb.Query()
        convert_to_dt = lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo = UTC)
        result = trending.search(query.queryTime.map(convert_to_dt) < thirty_days_ago)
        doc_ids = [r.doc_id for r in result]
        trending.remove(doc_ids = doc_ids)

        new_result = trending.search(query.queryTime.map(convert_to_dt) < thirty_days_ago)
        print(len(new_result))

    # with open(output_path + f"{time_str}_output.json", "w") as outfile:
    #     json.dump(response, outfile, indent = 4)

if __name__ == "__main__":
    main()
