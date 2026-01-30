import os
import ee
import json
import sys
from dotenv import load_dotenv

load_dotenv()

def test_gee():
    key_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    print(f"Key Path: {key_path}", flush=True)
    
    if not key_path or not os.path.exists(key_path):
        print("Key file not found!", flush=True)
        return

    try:
        with open(key_path) as f:
            content = json.load(f)
            print(f"Email: {content.get('client_email')}", flush=True)

        credentials = ee.ServiceAccountCredentials(
            email=content['client_email'],
            key_file=key_path
        )
        print("Initializing...", flush=True)
        ee.Initialize(credentials)
        print("SUCCESS: GEE Initialized!", flush=True)
        
        # Try a simple operation
        print(ee.String("Hello from GEE").getInfo(), flush=True)
        
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr, flush=True)

if __name__ == "__main__":
    test_gee()
