"""
MIT License

Copyright (c) 2025 Wen Lai (wen.lai@tum.de) and Yingli Shen (syl@mail.tsinghua.edu.cn).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software.

Note: The TED Talk transcripts and metadata collected by this tool are the property of TED and subject to TED’s content license (https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines).

"""

"""
#!/bin/bash

python fetch_latest_ids.py \
  --limit 2000 \
  --output_csv outputs/ted_talks_ids.csv

"""

import requests
import re
import json
import csv
import feedparser
from bs4 import BeautifulSoup
import argparse


TED_RSS = "https://www.ted.com/talks/rss"  # RSS feed URL


def get_latest_talk_urls(limit=5):
    """
    Parse TED RSS feed and return the latest talk URLs.
    """
    feed = feedparser.parse(TED_RSS)
    return [entry.link for entry in feed.entries[:limit]]


def extract_talk_id_from_html(html):
    """
    Attempt to extract TED Talk numeric ID from HTML using:
    1. JSON-LD script block
    2. __NEXT_DATA__ block
    3. Regex fallback
    """

    soup = BeautifulSoup(html, "html.parser")

    # 1) Try JSON-LD
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            obj = json.loads(script.string)

            def find_int(d):
                if isinstance(d, dict):
                    for v in d.values():
                        if isinstance(v, (int, float)):
                            return int(v)
                        if isinstance(v, str) and v.isdigit():
                            return int(v)
                        res = find_int(v)
                        if res:
                            return res
                elif isinstance(d, list):
                    for item in d:
                        res = find_int(item)
                        if res:
                            return res
                return None

            return find_int(obj)
        except Exception:
            pass

    # 2) Try __NEXT_DATA__
    for script in soup.find_all("script"):
        if script.string and "__NEXT_DATA__" in script.string[:100]:
            try:
                j = json.loads(script.string)

                def find_id(j):
                    if isinstance(j, dict):
                        for k, v in j.items():
                            if k.lower().endswith("id") and isinstance(v, (int, str)) and str(v).isdigit():
                                return int(v)
                            res = find_id(v)
                            if res:
                                return res
                    elif isinstance(j, list):
                        for item in j:
                            res = find_id(item)
                            if res:
                                return res
                    return None

                return find_id(j)
            except Exception:
                pass

    # 3) Fallback regex
    m = re.search(r'/talks/(\d+)', html)
    if m:
        return int(m.group(1))

    m = re.search(r'["\'](?:talk_id|id)["\']\s*[:=]\s*["\']?(\d+)', html)
    if m:
        return int(m.group(1))

    return None


def fetch_latest_ids(output_csv: str, limit: int = 5):
    """
    Fetch latest TED Talk URLs from RSS feed, extract talk IDs, and save to CSV.
    """
    urls = get_latest_talk_urls(limit)
    results = []

    for url in urls:
        print(f"[Fetch] {url}")
        try:
            response = requests.get(url, headers={"User-Agent": "ted-scraper/1.0"})
            talk_id = extract_talk_id_from_html(response.text)
        except Exception as e:
            print(f"[Error] Failed to fetch {url}: {e}")
            talk_id = None

        results.append((url, talk_id))

    # Write to CSV
    with open(output_csv, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Talk URL", "Talk ID"])
        for url, tid in results:
            writer.writerow([url, tid])

    print(f"\n✅ Saved {len(results)} entries to: {output_csv}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch latest TED Talks from RSS and extract Talk IDs.")
    parser.add_argument("--output_csv", type=str, default="outputs/ted_talks_ids.csv", help="Path to output CSV file")
    parser.add_argument("--limit", type=int, default=5, help="Number of latest talks to fetch")
    args = parser.parse_args()

    fetch_latest_ids(args.output_csv, args.limit)
