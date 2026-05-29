"""
downloader.py - Downloads WhatsApp media via Twilio CDN redirect
"""

import os
import uuid
import requests
from requests.auth import HTTPBasicAuth


def download_file(media_url: str, extension: str, account_sid: str, auth_token: str) -> str:
    os.makedirs("input", exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}{extension}"
    save_path = os.path.join("input", unique_name)

    print(f"📥 Fetching media...")

    # Step 1: Hit Twilio URL with auth → get 307 redirect to CDN
    r1 = requests.get(
        media_url,
        auth=HTTPBasicAuth(account_sid, auth_token),
        allow_redirects=False,
        timeout=30
    )
    print(f"   Twilio response: {r1.status_code}")

    if r1.status_code == 307:
        cdn_url = r1.headers.get('Location')
        print(f"   CDN URL: {cdn_url[:60]}...")
        # Step 2: Download from CDN WITHOUT auth
        r2 = requests.get(cdn_url, timeout=60, stream=True)
        print(f"   CDN download: {r2.status_code}")
        r2.raise_for_status()
        download_response = r2
    elif r1.status_code == 200:
        download_response = r1
    else:
        r1.raise_for_status()

    with open(save_path, "wb") as f:
        for chunk in download_response.iter_content(chunk_size=8192):
            f.write(chunk)

    size = os.path.getsize(save_path)
    print(f"✅ Downloaded: {save_path} ({size} bytes)")
    return save_path