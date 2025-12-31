#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON to CSV converter for Anki import
Converts 26225_Japanese.json to Anki-compatible CSV format
"""

import json
import csv

# Input and output files
INPUT_FILE = '26225_Japanese.json'
OUTPUT_FILE = '26225_Japanese.csv'

# Anki field headers (matching PLAN.md)
HEADERS = [
    'Frequency',
    'Expression',
    'Reading',
    'Meaning',
    'MeaningCount',
    'Exclude1',
    'Exclude2',
    'GenerateKR2JP',
    'GenerateJP2KR',
    'Image',
    'IMM_Sentence',
    'IMM_Image',
    'IMM_Audio',
    'IMM_SourceMedia'
]

def main():
    # Read JSON file
    print(f'Reading {INPUT_FILE}...')
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f'Found {len(data)} entries')

    # Write CSV file
    print(f'Writing {OUTPUT_FILE}...')
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, extrasaction='ignore')

        # Write header
        writer.writeheader()

        # Write rows
        for entry in data:
            # Create row with all fields
            row = {
                'Frequency': entry.get('Frequency', ''),
                'Expression': entry.get('Expression', ''),
                'Reading': entry.get('Reading', ''),
                'Meaning': entry.get('Meaning', ''),
                'MeaningCount': '',
                'Exclude1': '',
                'Exclude2': '',
                'GenerateKR2JP': '',
                'GenerateJP2KR': '',
                'Image': '',
                'IMM_Sentence': '',
                'IMM_Image': '',
                'IMM_Audio': '',
                'IMM_SourceMedia': ''
            }
            writer.writerow(row)

    print(f'Successfully converted {len(data)} entries to {OUTPUT_FILE}')
    print(f'File encoding: UTF-8')

if __name__ == '__main__':
    main()
