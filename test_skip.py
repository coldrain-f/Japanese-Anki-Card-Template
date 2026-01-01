#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick test to verify skip logic
"""

import csv

csv_path = 'resources/pos/noun.csv'

# Read CSV
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    headers = reader.fieldnames
    rows = list(reader)

total = len(rows)

# Filter out rows that already have meanings
to_process = []
to_process_indices = []
already_filled = 0

for idx, row in enumerate(rows):
    existing_meaning = row.get('Meaning', '').strip()
    if existing_meaning and '1.' in existing_meaning:
        already_filled += 1
        continue
    to_process.append(row)
    to_process_indices.append(idx)

print(f"Total entries: {total}")
print(f"Already filled (will skip): {already_filled}")
print(f"To process (empty): {len(to_process)}")
print(f"\nFirst 5 entries to process:")
for i, (idx, row) in enumerate(zip(to_process_indices[:5], to_process[:5])):
    print(f"  [{idx}] {row['Expression']} - Meaning: '{row.get('Meaning', '')}'")

print(f"\nFirst 5 filled entries (skipped):")
filled_count = 0
for idx, row in enumerate(rows):
    existing_meaning = row.get('Meaning', '').strip()
    if existing_meaning and '1.' in existing_meaning:
        print(f"  [{idx}] {row['Expression']} - Meaning: '{existing_meaning[:50]}...'")
        filled_count += 1
        if filled_count >= 5:
            break
