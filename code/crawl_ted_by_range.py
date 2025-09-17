"""
MIT License

Copyright (c) 2025 Wen Lai (wen.lai@tum.de) and Yingli Shen (syl@mail.tsinghua.edu.cn).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software.

Note: The TED Talk transcripts and metadata collected by this tool are the property of TED and subject to TED’s content license (https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines).

"""

"""
#!/bin/bash

# Run TED Talk scraper
python3 download_by_id_range.py \
  --start_id 0 \
  --end_id 100000 \
  --meta_output outputs/meta_data.jsonl \
  --output_dir outputs/transcripts \
  --resume
"""


import argparse
import requests
import time
import os
import json
from tqdm import tqdm
import subprocess
import random

# GraphQL query for TED Talk metadata
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
            primaryImageSet {
                url
            }
        }
    }
'''

QL_URL = 'https://www.ted.com/graphql'


def get_slug_by_id(talk_id):
    """Resolve TED Talk slug from numeric talk ID via redirect."""
    url = f"https://www.ted.com/talks/{talk_id}"
    try:
        response = requests.head(url, allow_redirects=False)
        if 300 < response.status_code < 400:
            redirected_url = response.headers.get('Location', '')
            if '/talks/' in redirected_url:
                slug = redirected_url.split('/talks/')[-1].strip('/')
                return slug
    except requests.exceptions.RequestException:
        pass
    return None


def get_json_by_slug(talk_slug):
    """Query TED GraphQL API for video metadata."""
    query_var = {"videoId": talk_slug}
    res = requests.post(QL_URL, json={"query": GETVIDEODATA_QUERY, "variables": query_var})

    if res.status_code != 200 or 'errors' in res.json():
        return None
    return res.json()


def download_transcript(slug, lang, output_dir):
    """Download transcript JSON for a given slug and language."""
    url = f"https://www.ted.com/talks/{slug}/transcript.json?language={lang}"
    slug_dir = os.path.join(output_dir, slug)
    os.makedirs(slug_dir, exist_ok=True)
    out_file = os.path.join(slug_dir, f"{lang}.json")

    if not os.path.exists(out_file):
        subprocess.call(f"wget -q -O {out_file} {url}", shell=True)


def main(args):
    start_id = args.start_id
    end_id = args.end_id
    meta_output_path = args.meta_output
    transcript_output_dir = args.output_dir

    # Resume from last processed ID if file exists
    if os.path.exists(meta_output_path) and args.resume:
        with open(meta_output_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines:
            try:
                last = json.loads(lines[-1])
                start_id = last.get("talk_id", start_id) + 1
            except Exception:
                pass

    os.makedirs(os.path.dirname(meta_output_path), exist_ok=True)
    os.makedirs(transcript_output_dir, exist_ok=True)

    with open(meta_output_path, "a+", encoding="utf-8") as meta_file:
        for talk_id in tqdm(range(start_id, end_id)):
            slug = get_slug_by_id(talk_id)
            if not slug:
                meta_file.write(json.dumps({"talk_id": talk_id}) + "\n")
                meta_file.flush()
                continue

            json_object = get_json_by_slug(slug)
            if not json_object:
                continue

            video_data = json_object["data"]["video"]
            langs = [
                e["node"]["internalLanguageCode"]
                for e in video_data.get("publishedSubtitleLanguages", {}).get("edges", [])
            ]
            topics = [
                n["name"]
                for n in video_data.get("topics", {}).get("nodes", [])
            ]
            images = video_data.get("primaryImageSet", [])
            image_urls = [img["url"] for img in images if "url" in img]

            record = {
                "talk_id": talk_id,
                "slug": slug,
                "title": video_data.get("title"),
                "author": video_data.get("presenterDisplayName"),
                "description": video_data.get("description"),
                "publishedAt": video_data.get("publishedAt"),
                "hasTranslations": video_data.get("hasTranslations"),
                "lang_list": langs,
                "topics": topics,
                "image_url": image_urls
            }

            for lang in langs:
                download_transcript(slug, lang, transcript_output_dir)

            meta_file.write(json.dumps(record) + "\n")
            meta_file.flush()
            time.sleep(random.uniform(0.1, 0.3))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape TED Talks by ID range")
    parser.add_argument("--start_id", type=int, default=0, help="Starting talk ID")
    parser.add_argument("--end_id", type=int, default=100000, help="Ending talk ID (exclusive)")
    parser.add_argument("--meta_output", type=str, default="outputs/meta_data.jsonl", help="Path to metadata output file")
    parser.add_argument("--output_dir", type=str, default="outputs/transcripts", help="Directory to save transcripts")
    parser.add_argument("--resume", action="store_true", help="Resume from last talk ID if file exists")
    args = parser.parse_args()

    main(args)
