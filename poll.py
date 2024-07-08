
import requests
from granary import atom, jsonfeed, microformats2, rss
import json
from tqdm import tqdm
import concurrent.futures
from urllib.parse import urlparse
import datetime
import os
from dateutil import parser

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

today = (datetime.datetime.now()  - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

with open("feeds.txt", "r") as f:
    feeds = f.read().splitlines()
    feeds = [feed.strip() for feed in feeds]

if os.path.exists("pages/_data/feed.json"):
    with open("pages/_data/feed.json", "r") as f:
        existing_feed = json.load(f)

        existing_posts = [post.get("id", "") for post in existing_feed if post and post.get("id")]

        print("Found", len(existing_posts), "existing posts")
else:
    existing_feed = []
    existing_posts = []

FEED_IDENTIFICATION = {
    "rss+xml": rss.to_activities,
    "atom+xml": atom.atom_to_activities,
    "html": microformats2.html_to_activities,
    "feed+json": jsonfeed.jsonfeed_to_activities,
    "json": jsonfeed.jsonfeed_to_activities,
    "mf2+json": microformats2.json_to_activities,
    "xml": rss.to_activities,
}

results = []

CONVERSION_FUNCTION = jsonfeed.activities_to_jsonfeed

def poll_feed(feed):
    try:
        resp = requests.get(
            feed, headers={"User-Agent": USER_AGENT}, allow_redirects=True, timeout=30
        )
    except requests.RequestException:
        print("Failed to fetch", feed)
        return []

    if resp.status_code != 200:
        print("Failed to fetch", feed, "with status code", resp.status_code)
        return []

    content_type = resp.headers.get("Content-Type", "").split(";")[0].split("/")[1]

    if content_type not in FEED_IDENTIFICATION:
        print("Unsupported feed type", content_type)
        return []

    if content_type in ["json", "feed+json"]:
        activities = CONVERSION_FUNCTION(FEED_IDENTIFICATION[content_type](resp.json())[0])
    else:
        activities = CONVERSION_FUNCTION(FEED_IDENTIFICATION[content_type](resp.text))

    items = activities.get("items", [])

    if not items:
        print("No items found in", feed)
        return []

    for item in items:
        if not item.get("url"):
            item["url"] = feed

        item["domain"] = urlparse(item.get("url")).netloc

        try:
            item["date_published"] = parser.parse(item.get("date_published", None)).strftime("%Y-%m-%d")
        except:
            item["date_published"] = today

        if item.get("content_html"):
            del item["content_html"]

    items = [item for item in items if item.get("id") and item["id"] not in existing_posts]

    print("Found", len(items), "new items in", feed)

    return items

with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(poll_feed, feeds))

results = [item for sublist in results for item in sublist]

for item in existing_feed:
    if item.get("id") not in existing_posts:
        results.append(item)

results = sorted(results, key=lambda x: x.get("date", ""), reverse=True)

with open("pages/_data/feed.json", "w+") as f:
    json.dump([result for result in results if result], f, indent=2)
