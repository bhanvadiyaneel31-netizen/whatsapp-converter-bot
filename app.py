"""
WhatsApp File Converter Bot
============================
Converts PDF <-> DOCX directly in WhatsApp using Twilio.
User sends a file → Bot replies with converted file.
"""

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(Path(__file__).parent / '.env')

import os
import requests
import traceback
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from downloader import download_file
from converter import convert_file

app = Flask(__name__)

# ── Twilio credentials (set these in .env or directly here for testing) ──
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "YOUR_ACCOUNT_SID")
TWILIO_AUTH_TOKEN  = os.environ.get("TWILIO_AUTH_TOKEN",  "YOUR_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")  # Twilio sandbox number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Twilio calls this URL every time a WhatsApp message arrives.
    We check if a file was attached, convert it, and reply.
    """
    resp = MessagingResponse()

    num_media = int(request.form.get("NumMedia", 0))
    print(f"🔑 SID being used: {TWILIO_ACCOUNT_SID[:10]}...")
    print(f"🔑 TOKEN being used: {TWILIO_AUTH_TOKEN[:10]}...")
    sender    = request.form.get("From")          # e.g. whatsapp:+919XXXXXXXXX

    # ── No file attached ──────────────────────────────────────────────────
    if num_media == 0:
        resp.message(
            "👋 Hello! I'm your *File Converter Bot*.\n\n"
            "📄 Send me a *PDF* → I'll give you a *Word Doc (.docx)*\n"
            "📝 Send me a *Word Doc (.docx)* → I'll give you a *PDF*\n\n"
            "Just attach a file and send!"
        )
        return str(resp)

    # ── File received ─────────────────────────────────────────────────────
    media_url         = request.form.get("MediaUrl0")
    media_content_type = request.form.get("MediaContentType0", "")

    # Detect file type from content type
    if "pdf" in media_content_type:
        incoming_ext = ".pdf"
    elif "word" in media_content_type or "docx" in media_content_type or \
         "officedocument" in media_content_type:
        incoming_ext = ".docx"
    else:
        resp.message(
            "⚠️ Sorry, I only support *PDF* and *Word (.docx)* files right now.\n"
            "Please send one of those!"
        )
        return str(resp)

    try:
        # Step 1 – Download the file from Twilio
        resp.message("⏳ Got your file! Converting... please wait a moment.")
        input_path = download_file(media_url, incoming_ext, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # Step 2 – Convert
        output_path = convert_file(input_path, incoming_ext)

        # Step 3 – Upload converted file to file.io and send download link
        output_ext = ".docx" if incoming_ext == ".pdf" else ".pdf"
        label      = "Word Doc (.docx)" if output_ext == ".docx" else "PDF"

        download_url = upload_to_fileio(output_path)

        client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=sender,
            body=(
                f"✅ Here's your converted *{label}*! 🎉\n\n"
                f"📥 *Download link* (expires in 14 days):\n{download_url}\n\n"
                f"_Tap the link to download your file._"
            )
        )

    except Exception as e:
        traceback.print_exc()
        resp.message(
            f"❌ Something went wrong during conversion.\n"
            f"Error: {str(e)}\n\nPlease try again!"
        )

    return str(resp)


def upload_to_fileio(file_path: str) -> str:
    """Upload to file.io and return download link."""
    try:
        with open(file_path, 'rb') as f:
            response = requests.post(
                'https://file.io',
                files={'file': (os.path.basename(file_path), f)},
                timeout=30
            )
        if 'application/json' in response.headers.get('Content-Type', ''):
            data = response.json()
            if data.get('success'):
                print(f"✅ Uploaded to file.io: {data['link']}")
                return data['link']
    except Exception as e:
        print(f"⚠️ file.io failed: {e}")

    # Fallback: serve via ngrok
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")
    filename = os.path.basename(file_path)
    fallback_url = f"{BASE_URL}/files/{filename}"
    print(f"📎 Using ngrok fallback: {fallback_url}")
    return fallback_url


def get_public_url(file_path: str) -> str:
    """
    Returns a public URL for the converted file.
    
    For LOCAL TESTING  → ngrok exposes localhost:5000
                         public URL = https://xxxx.ngrok.io/files/<filename>
    For PRODUCTION     → upload to Cloudinary / S3 / Render static files
    
    Update BASE_URL below with your ngrok URL when testing.
    """
    BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
    filename = os.path.basename(file_path)
    return f"{BASE_URL}/files/{filename}"


@app.route("/files/<filename>")
def serve_file(filename):
    """Serve converted files so Twilio can download and forward them."""
    from flask import send_from_directory
    return send_from_directory("output", filename)


if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    os.makedirs("input", exist_ok=True)
    print("🤖 WhatsApp Converter Bot is running on port 5000...")
    print("📡 Make sure ngrok is running: ngrok http 5000")
    app.run(debug=False, port=8080, host='0.0.0.0')