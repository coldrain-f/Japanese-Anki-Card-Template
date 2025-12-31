#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Debug script for "する" word
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--lang=ko-KR')

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

word = "する"
url = f"https://ja.dict.naver.com/#/search?range=word&query={word}"

print(f"Testing: {word}")
print(f"URL: {url}\n")

driver.get(url)
time.sleep(3)

# Save page source
with open('suru_page.html', 'w', encoding='utf-8') as f:
    f.write(driver.page_source)
print("[OK] Page source saved to suru_page.html")

# Try different selectors
selectors = [
    '.component_word',
    '.mean',
    '.mean_item',
    '[class*="component"]',
    '[class*="mean"]'
]

for selector in selectors:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        print(f"\n{selector}: Found {len(elements)} elements")
        if elements and len(elements) > 0:
            print(f"  First element text: {elements[0].text[:100]}")
    except Exception as e:
        print(f"\n{selector}: Error - {e}")

driver.quit()
