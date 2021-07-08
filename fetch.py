import json
import re

import psaw
import requests
import lxml.html


def fetch(all_ids=False):
    api = psaw.PushshiftAPI()
    # there is at least one post missing KotW in the title, therefore we search by selftext.
    try:
        with open('data/raw.json') as raw_file:
            raw_data = json.load(raw_file)
    except (FileNotFoundError, json.JSONDecodeError):
        raw_data = {}
    new_ids = []
    for post in api.search_submissions(subreddit='dominion', author='avocadro', selftext="Welcome to /r/dominion's Kingdom of the Week!"):
        # posts should be sorted by new, if current post has been previously processed, it is save to assume that there will be no other unprocessed post
        if post.id in raw_data.keys():
            break
        # most titles start with 'KotW \d+/\d+: ', there are only a handful of outliers
        title = re.sub(r'KotW:? \d+/\d+(?:/\d+)?:? ', '', post.title)
        raw_data[post.id] = title
        new_ids.append(post.id)
    with open('data/raw.json', 'w') as raw_file:
        json.dump(raw_data, raw_file, indent=2)
    # return ids of new posts
    return list(raw_data.keys()) if all_ids else new_ids


if __name__ == '__main__':
    fetch()
