import urllib.request
import urllib.parse
import re

def scrape_frequency(text):
    encoded_text = urllib.parse.quote(text)
    url = f"https://jpdb.io/search?q={encoded_text}&lang=english"
    
    try:
        print(f"Searching: {text.encode('utf-8', 'replace').decode('utf-8')}")
    except:
        print(f"Searching: (unicode)")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            matches = re.findall(r"Top\s+(\d+)", html)
            if matches:
                 print(f"  -> Found Ranks: {matches}")
            else:
                 print("  -> No 'Top X' found.")

    except Exception as e:
        print(f"Error: {e}")

scrape_frequency("今日") # Today
scrape_frequency("学校") # School
scrape_frequency("私")   # I / Me
scrape_frequency("日本") # Japan
