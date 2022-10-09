# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
import json

from reader import YouTubeReader
from datetime import datetime
from pytz import timezone

import googleapiclient.discovery
import googleapiclient.errors

def main():
    try:
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        api_key_path = "./api_key.txt"
        output_path = "./database/"

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
            regionCode="US"
        )
        response = request.execute()

        print("request executed")

        # Open the database
        YtR = YouTubeReader()
        # trending = database.table("TRENDING")

            # # Query and remove all documents 30 days or older
            # if False:
            #     thirty_days_ago = datetime.now(timezone("UTC")) - timedelta(days = 30)
            #     query = tinydb.Query()
            #     convert_to_dt = lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo = UTC)
            #     result = trending.search(query.queryTime.map(convert_to_dt) < thirty_days_ago)
            #     doc_ids = [r.doc_id for r in result]
            #     trending.remove(doc_ids = doc_ids)

        # Insert thew new videos
        YtR.insert_videos(response, "./database/yt_trending.xz")
        print("videos inserted")

        # Get the categories
        request = youtube.videoCategories().list(
            part="snippet",
            regionCode="US"
        )
        print("got the video categories")
        response = request.execute()
        with open(output_path + "video_categories.json", "w") as outfile:
            json.dump(response, outfile, indent = 2)

        print("done")

    # Something went wrong, log the exception
    except Exception as e:
        with open("./error.log", "a") as f:
            dt = datetime.now(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"{dt}: {type(e)}: {e}")
            f.write(f"{dt}: {type(e)}: {e}\n")

    # with open(output_path + f"{time_str}_output.json", "w") as outfile:
    #     json.dump(response, outfile, indent = 4)

if __name__ == "__main__":
    main()
