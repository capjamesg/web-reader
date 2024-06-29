
import requests
from granary import atom, jsonfeed, microformats2, rss
import json
from tqdm import tqdm
from urllib.parse import urlparse
import datetime
import os

USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"

today = datetime.datetime.now().strftime("%Y-%m-%d")

with open("feeds.txt", "r") as f:
    feeds = f.read().splitlines()
    feeds = [feed.strip() for feed in feeds]

if os.path.exists("pages/_data/feed.json"):
    with open("pages/_data/feed.json", "r") as f:
        existing_feed = json.load(f)

        existing_posts = [post.get("id", "") for post in existing_feed if post and post.get("id")]

        print("Found", len(existing_posts), "existing posts")
else:
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

for feed in tqdm(feeds):
    try:
        resp = requests.get(
            feed, headers={"User-Agent": USER_AGENT}, allow_redirects=True, timeout=30
        )
    except requests.RequestException:
        print("Failed to fetch", feed)
        continue

    if resp.status_code != 200:
        print("Failed to fetch", feed, "with status code", resp.status_code)
        continue

    content_type = resp.headers.get("Content-Type", "").split(";")[0].split("/")[1]

    if content_type not in FEED_IDENTIFICATION:
        print("Unsupported feed type", content_type)
        continue

    if content_type in ["json", "feed+json"]:
        activities = CONVERSION_FUNCTION(FEED_IDENTIFICATION[content_type](resp.json())[0])
    else:
        activities = CONVERSION_FUNCTION(FEED_IDENTIFICATION[content_type](resp.text))

    items = activities.get("items", [])

    if not items:
        print("No items found in", feed)
        continue

    domain = urlparse(feed).netloc

    for item in items:
        item["domain"] = domain
        
        if not item.get("date_published"):
            item["date_published"] = today
        
        # if not valid datestamp, replace
        try:
            datetime.datetime.strptime(item["date_published"], "%Y-%m-%d")
        except ValueError:
            item["date_published"] = today

        item["date_published"] = item["date_published"].split("T")[0].replace("-", "")

        if item.get("content_html"):
            del item["content_html"]

    items = [item for item in items if item.get("id") and item["id"] not in existing_posts]

    print("Found", len(items), "new items in", feed)

    results.extend(activities.get("items", []))

results = sorted(results, key=lambda x: x.get("date", ""), reverse=True)

with open("pages/_data/feed.json", "w+") as f:
    json.dump([result for result in results if result], f, indent=2)