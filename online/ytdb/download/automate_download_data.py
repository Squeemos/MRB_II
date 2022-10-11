"""Script for downloading data with the YouTube Data API client."""

import json

from ytdb.reader.reader import YouTubeReader
from datetime import datetime
from pytz import timezone

import googleapiclient.discovery
import googleapiclient.errors


def main():
    try:
        # Build client
        youtube = build_client()

        # Prepare I/O
        output_path = "./database/"
        youtube_reader = YouTubeReader()

        # Update trending videos
        get_trending(youtube, youtube_reader, output_path)

        # Update category ids
        category_ids = get_category_ids(youtube, output_path)

        # Update category videos
        get_categories(youtube, youtube_reader, output_path, category_ids)

        print("done")

    # Something went wrong, log the exception
    except Exception as e:
        with open("./error.log", "a") as f:
            dt = datetime.now(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"{dt}: {type(e)}: {e}")
            f.write(f"{dt}: {type(e)}: {e}\n")


def build_client():
    """Creates and returns the YouTube Data API client needed for requests."""
    print("building client...")

    api_key_path = "./api_key.txt"

    # API information
    api_service_name = "youtube"
    api_version = "v3"

    # Read API key
    with open(api_key_path, "r") as api_file:
        api_key = api_file.read()

    # Create the client with api_key
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key
    )
    print("client built")

    return youtube


def get_trending(youtube, youtube_reader, output_path: str, parts: str = None):
    """Gets top trending videos in the US."""
    print("getting trending videos...")

    if parts is None:
        parts = _get_all_parts()

    # Get data
    request = youtube.videos().list(
        part=parts,
        chart="mostPopular",
        maxResults=50,
        regionCode="US"
    )
    response = request.execute()
    print("got trending videos")

    # Insert the new videos into table
    youtube_reader.insert_videos(response, output_path + "yt_trending.xz")
    print("trending videos inserted")


def get_category_ids(youtube, output_path):
    """Saves raw response data for video categories and returns list of ids."""
    print("getting category ids...")

    request = youtube.videoCategories().list(
        part="snippet",
        regionCode="US"
    )
    response = request.execute()
    print("got category ids")

    with open(output_path + "video_categories.json", "w") as outfile:
        json.dump(response, outfile, indent=2)
    print("saved category ids")

    # Return categories
    category_ids = [cat["id"] for cat in response["items"]]

    return category_ids


def get_categories(youtube, youtube_reader, output_path, category_ids,
                   parts: str = None):
    """Gets top videos for all categories in the US that support this."""
    print("getting category videos...")

    if parts is None:
        parts = _get_all_parts()

    for cat_id in category_ids:
        try:
            # Get data
            request = youtube.videos().list(
                part=parts,
                chart="mostPopular",
                maxResults=50,
                regionCode="US",
                videoCategoryId=cat_id,
            )
            response = request.execute()
            print(f"got cat{cat_id} videos")

            # Insert the new videos into table
            youtube_reader.insert_videos(response, output_path + "yt_categories.xz")
            print(f"cat{cat_id} videos inserted")
        except googleapiclient.errors.HttpError:
            print(f"cat{cat_id} chart not found or failed")


def _get_all_parts():
    parts = (
        "id",
        "snippet",
        "contentDetails",
        "status",
        "statistics",
        "player",
        "topicDetails",
        "recordingDetails",
        "liveStreamingDetails",
        "localizations",
    )

    return ",".join(parts)


if __name__ == "__main__":
    main()
