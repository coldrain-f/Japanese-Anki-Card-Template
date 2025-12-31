#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POS (Part of Speech) classifier for Japanese words
Uses SudachiPy to classify words by their part of speech
Handles compound verbs as single words using SudachiPy's C mode
"""

import csv
from collections import defaultdict
from sudachipy import tokenizer, dictionary

# Input and output configuration
INPUT_FILE = 'resources/all/26225_Japanese.csv'
OUTPUT_DIR = 'resources/pos/'

# POS categories mapping (SudachiPy → simplified categories)
POS_CATEGORIES = {
    'noun': ['名詞'],
    'verb': ['動詞'],
    'adjective': ['形容詞', '形状詞'],
    'adverb': ['副詞'],
    'particle': ['助詞'],
    'auxiliary': ['助動詞'],
    'conjunction': ['接続詞'],
    'prefix': ['接頭辞'],
    'suffix': ['接尾辞'],
    'interjection': ['感動詞'],
    'others': []
}

def get_category(pos_major):
    """Map SudachiPy POS to category"""
    for category, pos_list in POS_CATEGORIES.items():
        if pos_major in pos_list:
            return category
    return 'others'

def analyze_word(tokenizer_obj, word):
    """
    Analyze word using SudachiPy
    Returns: (category, pos_detail)

    Uses SudachiPy C mode for longest tokenization
    This keeps compound verbs (like 思い出す) as single words
    """
    mode = tokenizer.Tokenizer.SplitMode.C  # Longest tokenization mode

    try:
        tokens = tokenizer_obj.tokenize(word, mode)

        if not tokens:
            return 'others', 'unknown'

        # Use the first (and usually only) token for single word analysis
        token = tokens[0]
        pos = token.part_of_speech()

        # pos is a tuple: (品詞大分類, 品詞中分類, 品詞小分類, 品詞細分類, ...)
        pos_major = pos[0] if pos else 'unknown'
        pos_detail = '-'.join(filter(None, pos[:4]))

        category = get_category(pos_major)

        return category, pos_detail

    except Exception as e:
        print(f"Warning: Failed to analyze '{word}': {e}")
        return 'others', 'error'

def main():
    print("=" * 60)
    print("Japanese POS Classifier using SudachiPy")
    print("=" * 60)

    # Initialize SudachiPy
    print("\nInitializing SudachiPy...")
    try:
        tokenizer_obj = dictionary.Dictionary(dict="full").create()
        print("[OK] SudachiPy initialized with FULL dictionary (C mode for compound words)")
    except Exception as e:
        print(f"[ERROR] Failed to initialize SudachiPy: {e}")
        print("\nPlease install SudachiPy:")
        print("  python -m pip install sudachipy sudachidict_full")
        return

    # Read input CSV
    print(f"\nReading {INPUT_FILE}...")
    rows_by_category = defaultdict(list)
    total_count = 0

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames

            for row in reader:
                expression = row.get('Expression', '').strip()

                if not expression:
                    continue

                # Analyze word
                category, pos_detail = analyze_word(tokenizer_obj, expression)

                # Add POS info as a comment (not saved in CSV)
                rows_by_category[category].append(row)
                total_count += 1

                # Progress indicator
                if total_count % 1000 == 0:
                    print(f"  Processed {total_count} words...")

    except FileNotFoundError:
        print(f"[ERROR] File not found: {INPUT_FILE}")
        return
    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return

    print(f"[OK] Analyzed {total_count} words")

    # Print statistics
    print("\n" + "=" * 60)
    print("Classification Results:")
    print("=" * 60)
    for category in sorted(rows_by_category.keys()):
        count = len(rows_by_category[category])
        percentage = (count / total_count * 100) if total_count > 0 else 0
        print(f"  {category:15s}: {count:6d} words ({percentage:5.2f}%)")

    # Create output directory
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Write CSV files by category
    print("\n" + "=" * 60)
    print("Writing CSV files:")
    print("=" * 60)

    for category, rows in sorted(rows_by_category.items()):
        output_file = os.path.join(OUTPUT_DIR, f"{category}.csv")

        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        print(f"  [OK] {output_file} ({len(rows)} entries)")

    print("\n" + "=" * 60)
    print("Classification complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
