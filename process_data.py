import json
import os
import pprint

if __name__ == '__main__':
    directory = "./data/"
    pp = pprint.PrettyPrinter(indent = 4)

    with open("./resources/video_categories.json", "r") as v_c:
        v_c_file = json.load(v_c)
        video_categories = {item["id"]:item["snippet"]["title"] for item in v_c_file["items"]}

    for file in os.listdir(directory):
        with open(directory + file, "r") as f:
            file_contents = json.load(f)
            items = file_contents["items"]
            for item in items:
                snippet = item["snippet"]
                statistics = item["statistics"]

                title = snippet["title"]
                description = snippet["description"]
                channel = snippet["channelTitle"]
                tags = snippet.get("tags", [])
                category_id = snippet["categoryId"]
                category = video_categories[category_id]

                view_count = int(statistics["viewCount"])
                comment_count = int(statistics["commentCount"])
                like_count = int(statistics["likeCount"])

                print(title, f"{view_count:,}", category)
