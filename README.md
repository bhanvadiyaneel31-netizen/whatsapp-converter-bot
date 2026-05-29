# 🤖 WhatsApp File Converter Bot

Convert PDF ↔ DOCX directly in WhatsApp — no app, no website needed.

---

## 🚀 What It Does

| You Send | Bot Replies With |
|---|---|
| 📄 PDF file | 📝 Word Doc (.docx) |
| 📝 Word Doc (.docx) | 📄 PDF file |

---

## 🛠️ Setup Guide (Step by Step)

### Step 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Install LibreOffice (for DOCX → PDF)

**Ubuntu/Linux (or Render.com):**
```bash
sudo apt update && sudo apt install -y libreoffice
```

**Mac:**
```bash
brew install libreoffice
```

**Windows:**
Download from https://www.libreoffice.org/download/download/

### Step 3 — Create a Twilio account (Free)

1. Go to https://www.twilio.com and sign up (free)
2. Go to **Messaging → Try it out → Send a WhatsApp message**
3. You'll get a sandbox number like `+14155238886`
4. Copy your **Account SID** and **Auth Token** from the dashboard

### Step 4 — Configure environment variables

```bash
cp .env.example .env
# Now edit .env and fill in your Twilio credentials
```

### Step 5 — Run the bot locally

```bash
python app.py
```

### Step 6 — Expose localhost using ngrok (Free)

In a NEW terminal:
```bash
# Install ngrok from https://ngrok.com (free)
ngrok http 5000
```

Copy the `https://xxxx.ngrok-free.app` URL.

Update your `.env`:
```
BASE_URL=https://xxxx.ngrok-free.app
```

### Step 7 — Set Webhook URL in Twilio

1. Go to Twilio Console → Messaging → Sandbox Settings
2. Set **"When a message comes in"** to:
   ```
   https://xxxx.ngrok-free.app/webhook
   ```
3. Method: `HTTP POST`
4. Save

### Step 8 — Join the Twilio Sandbox

On WhatsApp, message the sandbox number:
```
join <your-sandbox-keyword>
```
(Twilio shows this keyword in the sandbox settings)

### Step 9 — Test It!

Send any PDF or DOCX file to the WhatsApp sandbox number. The bot will reply with the converted file! 🎉

---

## 📁 Project Structure

```
whatsapp-converter-bot/
├── app.py           → Flask server + WhatsApp webhook
├── converter.py     → PDF ↔ DOCX conversion logic
├── downloader.py    → Downloads file from Twilio
├── requirements.txt → Python dependencies
├── .env.example     → Environment variables template
├── input/           → Temporary input files (auto-created)
└── output/          → Converted output files (auto-created)
```

---

## 🌐 Deploy for Free (Production)

Deploy to **Render.com** (free tier):

1. Push code to GitHub
2. Go to https://render.com → New Web Service
3. Connect your GitHub repo
4. Set environment variables in Render dashboard
5. Add build command: `pip install -r requirements.txt && apt-get install -y libreoffice`
6. Start command: `python app.py`
7. Copy the Render URL → paste in Twilio webhook settings

---

## 🔮 Future Extensions (Add These to Impress More)

- [ ] Image → PDF conversion
- [ ] Merge multiple PDFs into one
- [ ] Compress PDF (reduce file size)
- [ ] Extract text from PDF and send as message
- [ ] Support Excel → PDF
- [ ] Add usage counter / stats

---

## 🧑‍💻 Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.x | Core language |
| Flask | Web server / webhook receiver |
| Twilio | WhatsApp API |
| pdf2docx | PDF → DOCX conversion |
| LibreOffice | DOCX → PDF conversion |
| ngrok | Expose localhost for testing |

---

Built with ❤️ using Python
