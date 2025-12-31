#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script to check Naver API response
"""

import requests
import json
from urllib.parse import quote

# Test with a simple word
word = "思う"
encoded_word = quote(word)

print(f"Word: {word}")
print(f"Encoded: {encoded_word}")

api_url = f"https://ja.dict.naver.com/api/v1/search/word?query={encoded_word}&range=word"
print(f"\nAPI URL: {api_url}")

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8'
}

try:
    response = requests.get(api_url, headers=headers, timeout=10)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    if response.status_code == 200:
        # Save response to file for inspection
        with open('naver_response.json', 'w', encoding='utf-8') as f:
            json.dump(response.json(), f, ensure_ascii=False, indent=2)

        print("\n[OK] Response saved to naver_response.json")

        # Try to extract meaning
        data = response.json()

        if 'searchResultMap' in data:
            print("\n[OK] Found searchResultMap")
            result_map = data.get('searchResultMap', {})
            list_map = result_map.get('searchResultListMap', {})
            word_results = list_map.get('WORD', {})
            items = word_results.get('items', [])

            print(f"[INFO] Found {len(items)} items")

            if items:
                first_item = items[0]
                print(f"\n[INFO] First item keys: {first_item.keys()}")

                if 'meansCollector' in first_item:
                    means = first_item['meansCollector']
                    print(f"[INFO] Found {len(means)} meanings")

                    for i, m in enumerate(means[:3]):
                        if 'mean' in m:
                            print(f"  Meaning {i+1}: {m['mean']}")
        else:
            print("\n[FAIL] No searchResultMap in response")
    else:
        print(f"\n[FAIL] Request failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
