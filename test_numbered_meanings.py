#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test numbered meanings format
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_naver_meaning(driver, word):
    """Scrape meaning with numbered format (max 3 meanings)"""
    try:
        url = f"https://ja.dict.naver.com/#/search?range=word&query={word}"
        driver.get(url)

        # Wait for JavaScript to render
        time.sleep(2)
        wait = WebDriverWait(driver, 15)

        elements = None

        # Try to find the first search result container to avoid idioms/phrases
        try:
            first_entry = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.component_word'))
            )
            elements = first_entry.find_elements(By.CSS_SELECTOR, '.mean')
        except:
            pass

        # Fallback: just get all .mean elements
        if not elements or len(elements) == 0:
            try:
                elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.mean'))
                )
            except:
                return None

        if elements and len(elements) > 0:
            meanings = []
            for elem in elements[:3]:  # Maximum 3 meanings
                text = elem.text.strip()
                if text:
                    text = ' '.join(text.split())
                    meanings.append(text)

            if meanings:
                # Format: 1. ... 2. ... 3. ...
                numbered_meanings = [f"{i+1}. {meaning}" for i, meaning in enumerate(meanings)]
                return ' '.join(numbered_meanings)

        return None

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("Testing numbered meanings format\n")

    # Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('user-agent=Mozilla/5.0')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    test_words = ['する', 'ある', '思う', '人', 'こと']

    results = []

    try:
        for word in test_words:
            print(f"Testing: {word}")
            meaning = scrape_naver_meaning(driver, word)

            if meaning:
                results.append(f"{word}\n{meaning}\n")
                print("  [OK]")
            else:
                results.append(f"{word}\n[NOT FOUND]\n")
                print("  [FAIL]")

            time.sleep(1)

        # Save results
        with open('numbered_meanings_test.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(results))

        print("\n[OK] Results saved to numbered_meanings_test.txt")

    finally:
        driver.quit()

if __name__ == '__main__':
    main()
