#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scrape meanings from Naver Japanese Dictionary for all POS CSV files
Updates the Meaning field with numbered definitions (1. ... 2. ... 3. ...)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import os
import json
from pathlib import Path

# Configuration
POS_DIR = 'resources/pos/'
PROGRESS_FILE = 'scraping_progress.json'
DELAY_BETWEEN_REQUESTS = 1.5  # seconds
MAX_RETRIES = 3

# Files to process (only main POS)
TARGET_FILES = ['noun.csv', 'verb.csv', 'adjective.csv', 'adverb.csv']

def load_progress():
    """Load scraping progress from file"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    """Save scraping progress to file"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def scrape_naver_meaning(driver, word):
    """
    Scrape meaning from Naver Japanese Dictionary

    Args:
        driver: Selenium WebDriver instance
        word: Japanese word to look up

    Returns:
        Korean meaning string with numbers (1. ... 2. ... 3. ...) or None
        Maximum 3 meanings
    """
    try:
        url = f"https://ja.dict.naver.com/#/search?range=word&query={word}"
        driver.get(url)

        # Wait for the page to load (increased timeout and added sleep for stability)
        time.sleep(2)  # Allow JavaScript to render
        wait = WebDriverWait(driver, 15)

        elements = None

        # Try to find the first search result container to avoid idioms/phrases
        try:
            # Look for the first word entry
            first_entry = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.component_word'))
            )

            # Get mean elements only from the first entry
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
                    # Clean up text (remove extra whitespace)
                    text = ' '.join(text.split())
                    meanings.append(text)

            if meanings:
                # Format with numbers: 1. ... 2. ... 3. ...
                numbered_meanings = [f"{i+1}. {meaning}" for i, meaning in enumerate(meanings)]
                return ' '.join(numbered_meanings)

        return None

    except Exception as e:
        return None

def scrape_with_retry(driver, word, max_retries=MAX_RETRIES):
    """Scrape with retry logic"""
    for attempt in range(max_retries):
        meaning = scrape_naver_meaning(driver, word)
        if meaning:
            return meaning

        if attempt < max_retries - 1:
            time.sleep(1)  # Wait before retry

    return None

def process_csv_file(driver, csv_path, progress):
    """
    Process a single CSV file

    Args:
        driver: Selenium WebDriver
        csv_path: Path to CSV file
        progress: Progress dictionary

    Returns:
        Updated progress dictionary
    """
    filename = os.path.basename(csv_path)
    print(f"\n{'=' * 60}")
    print(f"Processing: {filename}")
    print(f"{'=' * 60}")

    # Read CSV
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    total = len(rows)
    completed = progress.get(filename, 0)

    print(f"Total entries: {total}")
    print(f"Starting from: {completed + 1}")

    # Process rows
    for i in range(completed, total):
        row = rows[i]
        expression = row.get('Expression', '').strip()

        if not expression:
            continue

        print(f"  [{i+1}/{total}] {expression}... ", end='', flush=True)

        # Scrape meaning
        meaning = scrape_with_retry(driver, expression)

        if meaning:
            row['Meaning'] = meaning
            print("[OK]")
        else:
            row['Meaning'] = ''
            print("[FAIL]")

        # Update progress
        progress[filename] = i + 1

        # Save progress every 10 entries
        if (i + 1) % 10 == 0:
            save_progress(progress)

            # Save intermediate results
            with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(rows)

        # Be polite to the server
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Save final results
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n[OK] Completed {filename}")
    return progress

def main():
    print("=" * 60)
    print("Naver Dictionary Scraper - Full Run")
    print("=" * 60)

    # Load progress
    progress = load_progress()

    # Get only target CSV files
    csv_files = [Path(POS_DIR) / filename for filename in TARGET_FILES]
    csv_files = [f for f in csv_files if f.exists()]

    if not csv_files:
        print(f"[ERROR] No target CSV files found in {POS_DIR}")
        return

    print(f"\nProcessing {len(csv_files)} CSV files:")
    total_entries = 0
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = sum(1 for row in reader)
            total_entries += count
            print(f"  - {csv_file.name}: {count:,} entries")

    print(f"\nTotal entries to process: {total_entries:,}")
    estimated_hours = (total_entries * DELAY_BETWEEN_REQUESTS) / 3600
    print(f"Estimated time: {estimated_hours:.1f} hours")

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
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

    try:
        # Process each CSV file
        for csv_file in csv_files:
            progress = process_csv_file(driver, str(csv_file), progress)
            save_progress(progress)

        print("\n" + "=" * 60)
        print("All files completed!")
        print("=" * 60)

        # Clean up progress file
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print("[OK] Progress file removed")

    except KeyboardInterrupt:
        print("\n\n[WARNING] Interrupted by user")
        print("[INFO] Progress has been saved. Run again to continue.")
        save_progress(progress)

    except Exception as e:
        print(f"\n[ERROR] {type(e).__name__}: {e}")
        save_progress(progress)

    finally:
        driver.quit()
        print("\n[INFO] WebDriver closed")

if __name__ == '__main__':
    main()
