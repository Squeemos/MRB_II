# -*- coding: utf-8 -*-

# Sample Python code for youtube.videos.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

import os
from datetime import date

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import json

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
secret_key_dir = "./secret_keys/"

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = secret_key_dir + os.listdir(secret_key_dir)[0]

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    commands = {
    0 : "Get top 50 videos",
    1 : "Get video categories",
    }

    print("What would you like to do")
    for key, value in commands.items():
        print(f"{key:2}: {value}")
    type = int(input())

    if type == 0:
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            chart="mostPopular",
            maxResults=50,
            regionCode="US",
            prettyPrint=True
        )
        response = request.execute()
        todays_date = date.today().strftime("%Y_%m_%d")
        with open(f"./data/{todays_date}_output.json", "w") as outfile:
            json.dump(response, outfile, indent = 4)

    elif type == 1:
        request = youtube.videoCategories().list(
            part="snippet",
            regionCode="US"
        )
        response = request.execute()
        with open(f"./resources/video_categories.json", "w") as outfile:
            json.dump(response, outfile, indent = 4)

if __name__ == "__main__":
    main()
