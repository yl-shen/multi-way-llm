"""
MIT License

Copyright (c) 2025 Wen Lai (wen.lai@tum.de) and Yingli Shen (syl@mail.tsinghua.edu.cn).

Permission is hereby granted, free of charge, to any person obtaining a copy of this software.

Note: The TED Talk transcripts and metadata collected by this tool are the property of TED and subject to TED’s content license (https://www.ted.com/about/our-organization/our-policies-terms/ted-content-guidelines).

"""

"""
#!/bin/bash

# Align multi-language transcripts
python3 align_transcripts.py \
  --input_dir outputs/transcripts \
  --output_file outputs/multi_way.jsonl

"""


import os
import json
from collections import defaultdict
from tqdm import tqdm
import argparse


def process_directory(root_dir, output_path):
    """
    Process transcript files from multiple languages,
    align them by timestamp, and write multi-way parallel data to a JSONL file.
    """
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for talk_id in tqdm(os.listdir(root_dir)):
            talk_path = os.path.join(root_dir, talk_id)

            if not os.path.isdir(talk_path):
                continue

            lang_files = defaultdict(list)

            # Load subtitle cues from each language
            for filename in os.listdir(talk_path):
                if filename.endswith('.json'):
                    lang = filename.split('.')[0]
                    file_path = os.path.join(talk_path, filename)

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)

                            # Extract all cue timestamps and texts
                            cues = []
                            for para in data.get('paragraphs', []):
                                for cue in para.get('cues', []):
                                    time = cue.get('time')
                                    text = cue.get('text')
                                    if time is not None and text:
                                        cues.append((time, text))
                            lang_files[lang] = cues
                    except Exception as e:
                        print(f"[Error] Failed to process {file_path}: {e}")
                        continue

            # Skip if fewer than two languages
            if len(lang_files) < 2:
                continue

            # Align by timestamps
            time_index = defaultdict(list)
            for lang, cues in lang_files.items():
                for time, text in cues:
                    time_index[time].append((lang, text))

            # Write parallel entries
            for timestamp, translations in time_index.items():
                if len(translations) < 2:
                    continue

                entry = {
                    "talk_id": talk_id,
                    "timestamp": timestamp,
                    "lang_list": [lang for lang, _ in translations],
                    "para_data": {lang: text for lang, text in translations},
                    "parallelism": len(translations)
                }

                outfile.write(json.dumps(entry, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Align TED transcripts into multi-way parallel data")
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing transcript folders')
    parser.add_argument('--output_file', type=str, required=True, help='Output JSONL file path')
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_file)