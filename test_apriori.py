from efficient_apriori import apriori
import os
import json
import string

def load_categories(path):
    with open(path) as v_c:
        v_c_file = json.load(v_c)
        return {item["id"]:item["snippet"]["title"] for item in v_c_file["items"]}

def remove_punctuation(text):
    processed = "".join([i for i in text if i not in string.punctuation])
    return processed

if __name__ == '__main__':
    directory = "./data/"

    video_categories = load_categories("./resources/video_categories.json")

    # create create baskets
    baskets = []
    with open(directory + "2022_09_06_output.json", "r") as f:
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

            title_p = remove_punctuation(title)
            title_p = title_p.lower()
            title_list = title_p.split(" ")
            title_list = [x for x in title_list if len(x)]

            baskets.append(title_list)

    min_support = .06
    min_confidence = 0.8

    itemsets, rules = apriori(baskets, min_support = min_support, min_confidence = min_confidence)
    #rules_rhs = filter(lambda rule: len(rule.lhs) == 2 and len(rule.rhs) == 1, rules)
    for rule in sorted(rules, key = lambda rule: rule.lift):
        print(rule)
