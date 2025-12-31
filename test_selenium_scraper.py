#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Selenium-based scraping for Naver Japanese Dictionary
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def scrape_naver_meaning_selenium(driver, word):
    """
    Scrape meaning using Selenium

    Args:
        driver: Selenium WebDriver instance
        word: Japanese word to look up

    Returns:
        Korean meaning string or None
    """
    try:
        url = f"https://ja.dict.naver.com/#/search?range=word&query={word}"

        driver.get(url)

        # Wait for the page to load
        wait = WebDriverWait(driver, 10)

        # Try different selectors that might contain the meaning
        selectors = [
            '.mean',
            '.mean_item',
            '.mean_txt',
            '[class*="mean"]',
            '.component_mean',
        ]

        for selector in selectors:
            try:
                # Wait for elements
                elements = wait.until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )

                if elements:
                    meanings = []
                    for elem in elements[:3]:
                        text = elem.text.strip()
                        if text and len(text) < 100:  # Reasonable length for a meaning
                            meanings.append(text)

                    if meanings:
                        print(f"  [DEBUG] Found with selector: {selector}")
                        return ', '.join(meanings)
            except:
                continue

        # If no specific selectors work, save page source for debugging
        print(f"  [DEBUG] No meanings found, saving page source...")

        return None

    except Exception as e:
        print(f"  [ERROR] {type(e).__name__}: {e}")
        return None

def main():
    print("=" * 60)
    print("Naver Dictionary Selenium Scraper - Test")
    print("=" * 60)

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # Initialize driver
    print("\nInitializing Chrome WebDriver...")
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        print("[OK] WebDriver initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize WebDriver: {e}")
        return

    # Test words
    test_words = ['する', '思う', 'ある']

    results = []

    try:
        for word in test_words:
            print(f"\nTesting: {word}")
            meaning = scrape_naver_meaning_selenium(driver, word)

            if meaning:
                results.append(f"{word}: {meaning}")
                print(f"  [OK] Found meaning")
            else:
                results.append(f"{word}: NOT FOUND")
                print(f"  [FAIL] Not found")

            time.sleep(1)  # Be polite

        # Save results to file
        with open('selenium_test_results.txt', 'w', encoding='utf-8') as f:
            for result in results:
                f.write(result + '\n')

        print("\n[OK] Results saved to selenium_test_results.txt")

    finally:
        driver.quit()
        print("\n" + "=" * 60)
        print("Test complete!")
        print("=" * 60)

if __name__ == '__main__':
    main()
