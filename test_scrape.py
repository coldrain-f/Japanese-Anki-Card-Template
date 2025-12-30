import urllib.request
import urllib.parse
import re

def scrape_frequency(text):
    encoded_text = urllib.parse.quote(text)
    url = f"https://jpdb.io/search?q={encoded_text}&lang=english"
    
    print(f"Searching: {text} -> {url}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Save to file for debug inspection
            # with open("debug_search.html", "w", encoding="utf-8") as f:
            #     f.write(html)
            
            # Pattern matching for frequency
            # Usually: <div class="tag">Top 1000</div> or similar.
            # Or inside the card details.
            
            # Let's search for "Top" and numbers
            # Example: "Top 1300"
            matches = re.findall(r"Top\s+(\d+)", html)
            if matches:
                 print(f"Found Top Ranks: {matches}")
                 # usually the first one is the main word if it's an exact match?
            else:
                 print("No 'Top X' found.")
                 
            # Check for "Frequency:" string if any
            if "Frequency" in html:
                print("String 'Frequency' found in HTML.")

    except Exception as e:
        print(f"Error: {e}")

print("--- Test Scraping ---")
scrape_frequency("本")
scrape_frequency("猫")
