import urllib.request
import urllib.error
import json
import re

API_KEY = "dd4acd6ad35807c979f0798c72878642"
API_URL = "https://jpdb.io/api/v1/parse"

def get_vocab_id(text):
    payload = {
        "text": text,
        "position_length_encoding": "utf16",
        "token_fields": ["vocab", "vocabulary_index"] 
    }
    # Note: trying "vocab" and "vocabulary_index".
    # Previous test said "vocab" failed. 
    # "vocabulary_index" succeeded.
    
    payload["token_fields"] = ["vocabulary_index"]

    req = urllib.request.Request(
        API_URL, 
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'
        }
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            tokens = data.get("tokens", [])
            if tokens:
                return tokens[0][0] # Assuming first token, first field
    except Exception as e:
        print(f"API Error for {text}: {e}")
    return None

def test_scrape(vid, text):
    if vid is None:
        print(f"Skipping scrape for {text} (No VID)")
        return

    # URL structure guess: https://jpdb.io/vocabulary/{vid}
    # Or https://jpdb.io/vocabulary/{vid}/{text}
    url = f"https://jpdb.io/vocabulary/{vid}/{urllib.parse.quote(text)}"
    print(f"Fetching {url}...")
    
    try:
        # Need headers probably to avoid bot detection?
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            # Look for "Frequency"
            # It usually says "Top 1300" or similar.
            
            # Simple fuzzy search
            match = re.search(r"Top\s+(\d+)", html)
            if match:
                print(f"Found Top Rank: {match.group(1)}")
            else:
                print("Could not find 'Top X' pattern.")
                
            # print snippet
            # print(html[:500])
            
    except Exception as e:
        print(f"Scrape Error: {e}")

words = ["本", "猫", "鉛筆", "食べる"]
for w in words:
    vid = get_vocab_id(w)
    print(f"Word: {w}, VID: {vid}")
    test_scrape(vid, w)
