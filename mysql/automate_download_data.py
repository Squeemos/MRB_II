"""Script for downloading data with the YouTube Data API client."""

import json

from reader import YouTubeReader
from datetime import datetime
from pytz import timezone

import googleapiclient.discovery
import googleapiclient.errors

def main():
    try:
        downloader = YoutubeDownloader("eric", "localhost", "mysql_key.txt", "./database/")

        # Update category ids
        category_ids = downloader.get_category_ids()

        # Update trending videos
        downloader.get_trending()

        # Update category videos
        downloader.get_categories(category_ids)

        print("done")

    # Something went wrong, log the exception
    except Exception as e:
        with open("./error.log", "a") as f:
            dt = datetime.now(timezone("UTC")).strftime("%Y-%m-%dT%H:%M:%SZ")
            print(f"{dt}: {type(e)}: {e}")
            f.write(f"{dt}: {type(e)}: {e}\n")

class YoutubeDownloader:
    def __init__(self, username: str, hostname: str, key_filename: str, output_path: str) -> None:
        # Build client
        self.youtube_client = self._build_client()

        # Prepare database info
        with open(key_filename, "r") as file:
            self.key = file.read()
        self.username = username
        self.hostname = hostname

        # Prepare file IO
        self.output_path = output_path

    def get_trending(self, parts: str = None):
        """Gets top trending videos in the US."""
        print("getting trending videos...")

        youtube_reader = YouTubeReader(self.username, self.key, self.hostname, "trending", "videos")

        if parts is None:
            parts = self._get_all_parts()

        # Get data
        request = self.youtube_client.videos().list(
            part=parts,
            chart="mostPopular",
            maxResults=50,
            regionCode="US"
        )
        response = request.execute()
        print("got trending videos")

        # Insert the new videos into table
        youtube_reader.insert_videos(response)
        print("trending videos inserted")

    def get_category_ids(self):
        """Saves raw response data for video categories and returns list of ids."""
        print("getting category ids...")

        request = self.youtube_client.videoCategories().list(
            part="snippet",
            regionCode="US"
        )
        response = request.execute()
        print("got category ids")

        with open(self.output_path + "video_categories.json", "w") as outfile:
            json.dump(response, outfile, indent=2)
        print("saved category ids")

        # Return categories
        category_ids = [cat["id"] for cat in response["items"]]

        return category_ids

    def get_categories(self, category_ids, parts: str = None):
        """Gets top videos for all categories in the US that support this."""
        print("getting category videos...")

        youtube_reader = YouTubeReader(self.username, self.key, self.hostname, "categories", "videos")

        if parts is None:
            parts = self._get_all_parts()

        for cat_id in category_ids:
            try:
                # Get data
                request = self.youtube_client.videos().list(
                    part=parts,
                    chart="mostPopular",
                    maxResults=50,
                    regionCode="US",
                    videoCategoryId=cat_id,
                )
                response = request.execute()
                print(f"got cat{cat_id} videos")

                # Insert the new videos into table
                youtube_reader.insert_videos(response)
                print(f"cat{cat_id} videos inserted")
            except googleapiclient.errors.HttpError:
                print(f"cat{cat_id} chart not found or failed")

        print("categories saved")

    @staticmethod
    def _build_client():
        """Creates and returns the YouTube Data API client needed for requests."""
        print("building client...")

        api_key_path = "api_key.txt"

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

    @staticmethod
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
