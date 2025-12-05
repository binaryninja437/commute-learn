# 🎧 Commute & Learn

**India's #1 Audio Study App for JEE/NEET Students**

Convert your handwritten notes and PDFs into engaging Hinglish audio podcasts with AI tutors Didi & Bhaiya!

![Commute & Learn](https://img.shields.io/badge/Made%20in-India%20🇮🇳-orange)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-MVP-blue)

---

## ✨ Features

- 📸 **Smart OCR** - Upload photos of handwritten notes or PDFs
- 🤖 **AI Script Generation** - Converts content to Hinglish conversation
- 🎙️ **Two-Voice Podcasts** - Didi (female) & Bhaiya (male) explain concepts
- 📱 **Spotify-style UI** - Beautiful, Gen-Z friendly dark theme
- 📥 **Offline Downloads** - MP3 files work anywhere

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- ffmpeg (for audio processing)

### 1. Clone & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/commute-learn.git
cd commute-learn

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install ffmpeg (Ubuntu/Debian)
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Frontend setup
cd ../frontend
npm install
```

### 2. Configure Environment

```bash
# In backend folder
cp .env.example .env

# Edit .env and add your Gemini API key
# Get free key at: https://makersuite.google.com/app/apikey
```

### 3. Run the App

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Open **http://localhost:3000** 🎉

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React + Vite)                  │
│              Spotify-style UI, Tailwind CSS                  │
│                    Port: 3000                                │
└─────────────────────┬───────────────────────────────────────┘
                      │ /api/*
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                         │
│                     Port: 8000                               │
│  Routes: /upload, /status, /download, /library               │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   ┌─────────┐  ┌──────────┐  ┌─────────┐
   │ Gemini  │  │  Script  │  │Edge TTS │
   │  OCR    │  │Generator │  │ Hindi   │
   │ (Free)  │  │ (Gemini) │  │ Voices  │
   └─────────┘  └──────────┘  └─────────┘
```

---

## 📁 Project Structure

```
commute-learn/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env.example         # Environment template
│   ├── services/
│   │   ├── ocr_service.py       # Text extraction (Gemini Vision)
│   │   ├── script_generator.py  # Hinglish script AI
│   │   └── tts_service.py       # Edge TTS (Hindi voices)
│   └── models/
│       └── schemas.py       # Pydantic models
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── src/
│       ├── main.jsx
│       ├── App.jsx          # Main React component
│       └── index.css        # Tailwind + custom styles
│
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload PDF/image, returns job_id |
| `GET` | `/api/status/{job_id}` | Get processing status |
| `GET` | `/api/download/{job_id}` | Download generated MP3 |
| `GET` | `/api/library` | List all generated podcasts |
| `DELETE` | `/api/podcast/{job_id}` | Delete a podcast |

---

## 🔧 Configuration

### Free API Tiers Used

| Service | Free Limit | Used For |
|---------|------------|----------|
| **Google Gemini** | 60 req/min | OCR + Script Generation |
| **Edge TTS** | Unlimited | Hindi Text-to-Speech |
| **PyMuPDF** | Open Source | PDF Processing |

### Voice Options (Edge TTS)

```python
# Hindi voices (configured in tts_service.py)
"DIDI": "hi-IN-SwaraNeural"    # Female, warm
"BHAIYA": "hi-IN-MadhurNeural"  # Male, energetic

# Indian English alternatives
"DIDI": "en-IN-NeerjaNeural"
"BHAIYA": "en-IN-PrabhatNeural"
```

---

## 🛣️ Roadmap

### V1.0 (Current) - MVP
- [x] Upload PDF/Image
- [x] OCR with Gemini Vision
- [x] Hinglish script generation
- [x] Two-voice TTS podcast
- [x] Spotify-style player

### V1.1 - Quality
- [ ] Better voice quality (Sarvam AI)
- [ ] Quiz generation from content
- [ ] Flashcard export

### V1.2 - Growth
- [ ] User authentication
- [ ] Razorpay payments (₹5/podcast)
- [ ] WhatsApp sharing
- [ ] Preloaded NCERT chapters

### V2.0 - Scale
- [ ] Mobile app (React Native)
- [ ] Offline sync
- [ ] AdMob integration
- [ ] Multi-language (Tamil, Telugu, Marathi)

---

## 💰 Monetization Strategy

| Tier | Price | Features |
|------|-------|----------|
| **Free** | ₹0 | 1 podcast/day, ads |
| **Pro** | ₹99/mo | Unlimited, no ads, quiz |
| **Per-use** | ₹5/podcast | One-time unlock |

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📜 License

MIT License - feel free to use for your own projects!

---

## 🙏 Credits

- **Google Gemini** - OCR & AI
- **Microsoft Edge TTS** - Hindi voices
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

---

<p align="center">
  <b>Made with ❤️ for Indian students</b><br>
  <i>Padhai ka naya tareeka! 📚🎧</i>
</p>
