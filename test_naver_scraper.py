#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for Naver Japanese Dictionary scraping
Tests the scraping functionality with a few sample words
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote

def scrape_naver_meaning(word):
    """
    Scrape meaning from Naver Japanese Dictionary

    Args:
        word: Japanese word to look up

    Returns:
        Korean meaning string or None if not found
    """
    # Use the search page URL
    encoded_word = quote(word)
    url = f"https://ja.dict.naver.com/#/search?range=word&query={encoded_word}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8'
    }

    try:
        # Try API endpoint first
        api_url = f"https://ja.dict.naver.com/api/v1/search/word?query={encoded_word}&range=word"

        response = requests.get(api_url, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()

                # Navigate the JSON structure
                if 'searchResultMap' in data:
                    result_map = data.get('searchResultMap', {})
                    list_map = result_map.get('searchResultListMap', {})
                    word_results = list_map.get('WORD', {})
                    items = word_results.get('items', [])

                    if items:
                        first_item = items[0]
                        means = first_item.get('meansCollector', [])

                        meanings = [m.get('mean', '') for m in means if 'mean' in m]

                        if meanings:
                            # Return top 3 meanings
                            return ', '.join(meanings[:3])

            except Exception as json_error:
                pass  # Fall through to HTML parsing

        # If API fails, try HTML scraping
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for meaning elements (this may need adjustment based on actual HTML)
            meanings = []
            mean_elements = soup.select('.mean')

            for elem in mean_elements[:3]:
                text = elem.get_text(strip=True)
                if text:
                    meanings.append(text)

            if meanings:
                return ', '.join(meanings)

        return None

    except Exception as e:
        print(f"Error scraping '{word}': {type(e).__name__}: {e}")
        return None

def main():
    # Test words
    test_words = ['する', '思う', 'ある', 'こと', '人', '今']

    print("=" * 60)
    print("Naver Dictionary Scraper - Test")
    print("=" * 60)

    for word in test_words:
        print(f"\nTesting: {word}")
        meaning = scrape_naver_meaning(word)

        if meaning:
            print(f"  [OK] Found: {meaning}")
        else:
            print(f"  [FAIL] Not found")

        # Be polite to the server
        time.sleep(0.5)

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
