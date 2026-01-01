#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel scraper for Naver Japanese Dictionary
Uses multiple WebDriver instances to scrape faster
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
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
POS_DIR = 'resources/pos/'
PROGRESS_FILE = 'scraping_progress_parallel.json'
NUM_WORKERS = 10  # Number of parallel browsers
DELAY_BETWEEN_REQUESTS = 0.1  # Minimal delay per worker
MAX_RETRIES = 2

# Files to process
TARGET_FILES = ['noun.csv', 'verb.csv', 'adjective.csv', 'adverb.csv']

# Thread-safe lock for file operations
file_lock = threading.Lock()
progress_lock = threading.Lock()

def load_progress():
    """Load scraping progress from file"""
    with progress_lock:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    return {}

def save_progress(progress):
    """Save scraping progress to file"""
    with progress_lock:
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)

def create_driver():
    """Create a new WebDriver instance with maximum optimization"""
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')  # New headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--lang=ko-KR')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')

    # Performance optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-plugins')
    chrome_options.add_argument('--disable-images')  # Don't load images
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-javascript-harmony')
    chrome_options.add_argument('--disable-sync')
    chrome_options.add_argument('--disable-translate')
    chrome_options.add_argument('--disable-default-apps')
    chrome_options.add_argument('--no-first-run')
    chrome_options.add_argument('--no-default-browser-check')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--disable-permissions-api')
    chrome_options.add_argument('--ignore-certificate-errors')

    # Page load strategy
    chrome_options.page_load_strategy = 'eager'  # Don't wait for full page load

    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    # Set timeouts
    driver.set_page_load_timeout(10)
    driver.set_script_timeout(10)

    return driver

def scrape_naver_meaning(driver, word):
    """Scrape meaning from Naver Japanese Dictionary"""
    try:
        url = f"https://ja.dict.naver.com/#/search?range=word&query={word}"
        driver.get(url)

        wait = WebDriverWait(driver, 3)
        elements = None

        # Try to find the first word entry
        try:
            first_entry = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.component_word'))
            )
            elements = first_entry.find_elements(By.CSS_SELECTOR, '.mean')
        except:
            pass

        # Fallback
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
                numbered_meanings = [f"{i+1}. {meaning}" for i, meaning in enumerate(meanings)]
                return ' '.join(numbered_meanings)

        return None

    except Exception as e:
        return None

def scrape_with_retry(driver, word):
    """Scrape with retry logic"""
    for attempt in range(MAX_RETRIES):
        meaning = scrape_naver_meaning(driver, word)
        if meaning:
            return meaning
        if attempt < MAX_RETRIES - 1:
            time.sleep(0.2)
    return None

def worker_task(worker_id, rows_chunk, indices, filename, all_rows, headers, csv_path):
    """Worker function to process a chunk of rows"""
    driver = None
    results = []

    try:
        driver = create_driver()
        print(f"[Worker {worker_id}] Started with {len(rows_chunk)} entries")

        for idx, (row_idx, row) in enumerate(zip(indices, rows_chunk)):
            expression = row.get('Expression', '').strip()

            if not expression:
                results.append((row_idx, row, ''))
                continue

            # Skip if meaning already exists
            existing_meaning = row.get('Meaning', '').strip()
            if existing_meaning and '1.' in existing_meaning:
                results.append((row_idx, row, '[SKIP]'))
                # No delay for skipped entries
                continue

            # Scrape meaning
            meaning = scrape_with_retry(driver, expression)

            if meaning:
                row['Meaning'] = meaning
                status = "[OK]"
            else:
                row['Meaning'] = ''
                status = "[FAIL]"

            results.append((row_idx, row, status))

            # Update main rows array and save every 50 entries
            if (idx + 1) % 50 == 0:
                with file_lock:
                    # Update rows
                    for r_idx, updated_row, _ in results:
                        all_rows[r_idx] = updated_row

                    # Save to CSV
                    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=headers)
                        writer.writeheader()
                        writer.writerows(all_rows)

                    results = []  # Clear processed results

                print(f"[Worker {worker_id}] Progress: {idx+1}/{len(rows_chunk)} (saved)")

            # Progress indicator
            elif (idx + 1) % 10 == 0:
                print(f"[Worker {worker_id}] Progress: {idx+1}/{len(rows_chunk)}")

            # Only delay if we actually scraped
            time.sleep(DELAY_BETWEEN_REQUESTS)

        print(f"[Worker {worker_id}] Completed!")

    except Exception as e:
        print(f"[Worker {worker_id}] Error: {e}")

    finally:
        if driver:
            driver.quit()

    return results

def process_csv_file_parallel(csv_path, progress, num_workers=NUM_WORKERS):
    """Process CSV file with parallel workers"""
    filename = os.path.basename(csv_path)
    print(f"\n{'=' * 60}")
    print(f"Processing: {filename}")
    print(f"{'=' * 60}")

    # Read CSV
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)

    total = len(rows)

    # Filter out rows that already have meanings (skip filled entries)
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
    print(f"Already filled: {already_filled}")
    print(f"To process: {len(to_process)}")
    print(f"Workers: {num_workers}")

    if len(to_process) == 0:
        print(f"[INFO] {filename} already completed, skipping")
        progress[filename] = total
        return progress

    # Use filtered rows
    remaining_rows = to_process
    remaining_indices = to_process_indices

    # Split into chunks for workers
    chunk_size = len(remaining_rows) // num_workers
    if chunk_size == 0:
        chunk_size = 1

    chunks = []
    index_chunks = []
    for i in range(0, len(remaining_rows), chunk_size):
        chunks.append(remaining_rows[i:i+chunk_size])
        index_chunks.append(remaining_indices[i:i+chunk_size])

    print(f"[INFO] Split into {len(chunks)} chunks")

    # Process in parallel
    all_results = []

    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for worker_id, (chunk, indices) in enumerate(zip(chunks, index_chunks)):
            future = executor.submit(worker_task, worker_id, chunk, indices, filename, rows, headers, csv_path)
            futures.append(future)

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                print(f"[ERROR] Worker failed: {e}")

    # Update rows with final results (if any remaining)
    if all_results:
        for row_idx, updated_row, status in all_results:
            rows[row_idx] = updated_row

    # Save final results
    print(f"\n[INFO] Saving final results to {filename}...")
    with file_lock:
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

    # Update progress
    progress[filename] = total
    save_progress(progress)

    print(f"[OK] Completed {filename}")
    return progress

def main():
    print("=" * 60)
    print("Naver Dictionary Scraper - PARALLEL MODE")
    print("=" * 60)

    # Load progress
    progress = load_progress()

    # Get target CSV files
    csv_files = [Path(POS_DIR) / filename for filename in TARGET_FILES]
    csv_files = [f for f in csv_files if f.exists()]

    if not csv_files:
        print(f"[ERROR] No target CSV files found in {POS_DIR}")
        return

    print(f"\nProcessing {len(csv_files)} CSV files with {NUM_WORKERS} parallel workers:")
    total_entries = 0
    for csv_file in csv_files:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = sum(1 for row in reader)
            completed = progress.get(csv_file.name, 0)
            remaining = count - completed
            total_entries += remaining
            print(f"  - {csv_file.name}: {remaining:,} remaining (of {count:,})")

    print(f"\nTotal remaining entries: {total_entries:,}")

    # Estimate time
    estimated_seconds = (total_entries / NUM_WORKERS) * (DELAY_BETWEEN_REQUESTS + 2)
    estimated_hours = estimated_seconds / 3600
    print(f"Estimated time: {estimated_hours:.1f} hours")

    try:
        # Process each CSV file
        for csv_file in csv_files:
            progress = process_csv_file_parallel(str(csv_file), progress, NUM_WORKERS)

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

if __name__ == '__main__':
    main()
