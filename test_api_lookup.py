import urllib.request
import urllib.error
import json

API_KEY = "dd4acd6ad35807c979f0798c72878642"

# Candidate URLs
URLS = [
    "https://jpdb.io/api/v1/lookup-vocabulary",
    "https://jpdb.io/api/v1/vocabulary/lookup",
    "https://jpdb.io/api/v1/lookup",
    "https://jpdb.io/api/v1/deck/lookup-vocabulary"
]

def test_lookup(vid):
    print(f"\n--- Testing Lookup for VID: {vid} ---")
    
    # Payload patterns
    payloads = [
        {"list": [vid], "fields": ["frequency_rank"]},
        {"ids": [vid], "fields": ["frequency_rank"]},
        {"id": [vid], "fields": ["frequency_rank"]},
        {"list": [vid], "fields": ["frequency"]}, # maybe field name differs?
        {"list": [vid]} # minimal
    ]
    
    for url in URLS:
        print(f"\nTesting URL: {url}")
        for i, p in enumerate(payloads):
            # print(f"  P{i}: {json.dumps(p)}")
            req = urllib.request.Request(
                url, 
                data=json.dumps(p).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {API_KEY}',
                    'Content-Type': 'application/json'
                }
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode('utf-8'))
                    print(f"  SUCCESS at {url} with payload {i}")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                    return # Stop if found
            except urllib.error.HTTPError as e:
                # print(f"  FAILED: {e.code}")
                if e.code != 404:
                     # If it's not 404, the URL might be right but payload wrong
                     print(f"  FAILED {url} Code: {e.code}")
                     # try:
                     #    print(f"  Body: {e.read().decode('utf-8')}")
                     # except: pass
            except Exception as e:
                print(f"  Error: {e}")

# Use a hardcodded VID if 0 was failing, but 0 is what we got.
# Let's try grabbing a fresh VID for "本" (Book) again.
# If 0 is valid, we use 0. If 0 is invalid, we might need another word.
# Let's try parsing "猫" (Cat) to see if it's different.

def get_vid(text):
    url = "https://jpdb.io/api/v1/parse"
    payload = {
        "text": text,
        "token_fields": ["vocabulary_index"],
        "position_length_encoding": "utf16"
    }
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'),
        headers={'Authorization': f'Bearer {API_KEY}','Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as r:
            d = json.loads(r.read())
            return d['tokens'][0][0]
    except:
        return 0

vid_cat = get_vid("猫")
print(f"VID for 猫: {vid_cat}")

if vid_cat != 0:
    test_lookup(vid_cat)
else:
    # If even Cat is 0, then 0 might be "unknown" or API is weird.
    # Let's try lookup with 0 anyway.
    test_lookup(0)
