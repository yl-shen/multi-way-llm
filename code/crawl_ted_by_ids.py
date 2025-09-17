"""
MIT License

Copyright (c) 2025 Wen Lai (wen.lai@tum.de) and Yingli Shen (syl@mail.tsinghua.edu.cn).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software.

Note: The TED Talk transcripts and metadata collected by this tool are the property of TED and subject to TED’s content license (https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines).

"""

"""
#!/bin/bash

# Run TED Talk scraper
python3 download_by_latest_id.py \
  --input_csv data/ted_talks_ids.csv \
  --meta_output outputs/meta_data.jsonl \
  --output_dir outputs/transcripts
"""

import argparse
import csv
import requests
import time
import os
import json
from tqdm import tqdm
import subprocess
import random

# GraphQL query to get TED video metadata
GETVIDEODATA_QUERY = '''
    query ($videoId:ID!){
        video(id: $videoId){
            title
            slug
            description
            presenterDisplayName
            publishedAt
            hasTranslations
            publishedSubtitleLanguages{
                edges{
                    node{
                        internalLanguageCode
                    }
                }
            }
            topics{
                nodes {
                    name
                }
            }
        }
    }
'''

QL_URL = 'https://www.ted.com/graphql'


def read_talk_ids_from_csv(csv_path):
    """Read TED Talk IDs from a CSV file."""
    ids = []
    with open(csv_path, newline='', encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                tid = int(row["Talk ID"])
                ids.append(tid)
            except (KeyError, ValueError):
                continue
    return ids


def get_slug_by_id(talk_id):
    """Resolve TED slug from talk ID via HTTP redirect."""
    url = f"https://www.ted.com/talks/{talk_id}"
    try:
        response = requests.head(url, allow_redirects=False)
        if 300 < response.status_code < 400:
            redirected_url = response.headers.get('Location', '')
            if '/talks/' in redirected_url:
                slug = redirected_url.split('/talks/')[-1].strip('/')
                return slug
        return None
    except requests.exceptions.RequestException:
        return None


def get_json_by_slug(talk_slug):
    """Query TED GraphQL API to get metadata by slug."""
    query_var = {"videoId": talk_slug}
    res = requests.post(QL_URL, json={"query": GETVIDEODATA_QUERY, "variables": query_var})

    if res.status_code != 200 or 'errors' in res.json():
        return None

    return res.json()


def down_transcript(slug, lang, out_path):
    """Download TED Talk transcript JSON for a given language."""
    base_url = "https://www.ted.com/talks"
    down_url = f"{base_url}/{slug}/transcript.json?language={lang}"
    slug_dir = os.path.join(out_path, slug)
    os.makedirs(slug_dir, exist_ok=True)
    out_file = os.path.join(slug_dir, f"{lang}.json")

    if not os.path.exists(out_file):
        down_cmd = f"wget -q -O {out_file} {down_url}"
        subprocess.call(down_cmd, shell=True)


def main(args):
    talk_id_list = read_talk_ids_from_csv(args.input_csv)

    # Read already processed talk IDs
    processed_ids = set()
    if os.path.exists(args.meta_output):
        with open(args.meta_output, "r", encoding="utf-8") as fr:
            lines = fr.readlines()
        processed_ids = {json.loads(line).get("talk_id") for line in lines if "talk_id" in json.loads(line)}

    with open(args.meta_output, "a+", encoding="utf-8") as meta_file:
        for talk_id in tqdm(talk_id_list):
            if talk_id in processed_ids:
                continue

            slug = get_slug_by_id(talk_id)
            if slug:
                json_object = get_json_by_slug(slug)
                if not json_object:
                    continue

                video_data = json_object["data"]["video"]
                lang_list = [e["node"]["internalLanguageCode"] for e in video_data.get("publishedSubtitleLanguages", {}).get("edges", [])]
                topics = [n["name"] for n in video_data.get("topics", {}).get("nodes", [])]

                record = {
                    "talk_id": talk_id,
                    "slug": slug,
                    "title": video_data.get("title"),
                    "author": video_data.get("presenterDisplayName"),
                    "description": video_data.get("description"),
                    "publishedAt": video_data.get("publishedAt"),
                    "hasTranslations": video_data.get("hasTranslations"),
                    "lang_list": lang_list,
                    "topics": topics
                }

                for lang in lang_list:
                    down_transcript(slug, lang, args.output_dir)

            else:
                record = {"talk_id": talk_id}

            meta_file.write(json.dumps(record) + "\n")
            meta_file.flush()
            time.sleep(random.uniform(0.1, 0.3))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TED Talk Transcript Scraper")
    parser.add_argument("--input_csv", type=str, default="data/ted_talks_ids.csv", help="Path to CSV containing TED Talk IDs")
    parser.add_argument("--meta_output", type=str, default="outputs/meta_data.jsonl", help="Path to output metadata JSONL file")
    parser.add_argument("--output_dir", type=str, default="outputs/transcripts", help="Directory to save downloaded transcripts")
    args = parser.parse_args()

    main(args)
