# 🚀 SaarLM Quick Start Guide

## Current Working Configuration (Dec 12, 2024)

- **Backend:** http://localhost:8001
- **Frontend:** http://localhost:3002
- **Status:** ✅ Fully Working

---

## Start the App

### 1. Start Backend (Terminal 1)
```bash
cd commute-learn/backend
set PYTHONIOENCODING=utf-8
venv311/Scripts/python.exe -m uvicorn main:app --reload --port 8001
```

**Important:** Always set `PYTHONIOENCODING=utf-8` before starting!

### 2. Start Frontend (Terminal 2)
```bash
cd commute-learn/frontend
npm run dev
```

Frontend will auto-start on port 3002 (or next available).

### 3. Open Browser
Navigate to: **http://localhost:3002**

---

## How to Use SaarLM

### Upload Notes
1. Click "Upload New Notes" or drag-and-drop an image/PDF
2. Enter Subject (e.g., "Physics")
3. Enter Chapter (e.g., "Gravitation")
4. Click "Start Processing"

### Processing Steps
- **OCR:** Extracting text from image (20-30 seconds)
- **Script:** Generating Hinglish podcast script (30-60 seconds)
- **TTS:** Creating audio with voices (60-90 seconds)

### Listen to Podcast
- Automatic transition to player when complete
- Play/pause, seek, download options
- View full script below player

---

## Troubleshooting

### Problem 1: "Internal Server Error"
**Solution:** Restart backend with UTF-8 encoding
```bash
cd commute-learn/backend
set PYTHONIOENCODING=utf-8
venv311/Scripts/python.exe -m uvicorn main:app --reload --port 8001
```

### Problem 2: Upload stuck at "Processing..."
**Check:**
1. Backend logs for errors
2. Gemini API key in `.env` file
3. API quota not exhausted

**Quick Fix:** Refresh browser and try again

### Problem 3: Podcast not loading after upload
**Solution:** Frontend already accepts both status types. Just refresh browser.

### Problem 4: Port already in use
**Backend port 8001 busy:**
```bash
netstat -ano | findstr :8001
powershell -Command "Stop-Process -Id [PID] -Force"
```

**Frontend auto-finds next port** (3002, 3003, etc.)

---

## Emergency Restore

If something breaks:

### Windows
1. Double-click: `backend/backups/restore.bat`
2. Follow on-screen instructions

### Linux/Mac
```bash
bash backend/backups/restore.sh
```

This restores all files to last working version (Dec 12, 2024).

---

## Environment Variables

File: `backend/.env`
```env
GEMINI_API_KEY=AIzaSyCAihYrPAf7eGfyqveAFOE-XQwPnUAk2-k
PORT=8001
```

**Note:** Keep API key secure! Don't commit to public repos.

---

## Features

### ✅ Working Features
- Image/PDF upload with drag-and-drop
- OCR text extraction (Gemini Vision API)
- Hinglish podcast script generation
- Multi-voice TTS (Didi & Bhaiya characters)
- Audio playback with progress bar
- Library view of all podcasts
- Download audio files
- Delete podcasts

### 🎨 UI Features
- Spotify-like dark theme
- Responsive design
- Real-time processing status
- Animated progress indicators
- Beautiful podcast cards

---

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- Google Gemini 2.5 Flash API
- gTTS (Google Text-to-Speech)
- pydub (audio processing)

### Frontend
- React 18
- Vite
- Tailwind CSS
- Lucide Icons

---

## File Structure

```
commute-learn/
├── backend/
│   ├── main.py                 # Main FastAPI app
│   ├── services/
│   │   ├── ocr_service.py      # Gemini Vision OCR
│   │   ├── script_generator.py # Script generation
│   │   └── tts_service.py      # Text-to-Speech
│   ├── backups/                # Working file backups
│   │   ├── README.md
│   │   ├── restore.sh
│   │   ├── restore.bat
│   │   └── [backup files]
│   ├── uploads/                # User uploaded files
│   ├── outputs/                # Generated audio files
│   ├── metadata/               # Podcast metadata JSON
│   └── .env                    # API keys
│
└── frontend/
    ├── src/
    │   ├── App.jsx             # Main React component
    │   └── index.css           # Tailwind styles
    └── package.json
```

---

## Testing Checklist

Before deploying or making changes:

- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3002
- [ ] Upload accepts images/PDFs
- [ ] OCR extracts text correctly
- [ ] Script generated in Hinglish
- [ ] Audio file plays correctly
- [ ] Podcast displays in player
- [ ] Library shows all podcasts
- [ ] Download works
- [ ] Delete works

---

## Common Commands

### Backend
```bash
# Start server
cd backend
set PYTHONIOENCODING=utf-8
venv311/Scripts/python.exe -m uvicorn main:app --reload --port 8001

# Check API key
cd backend
cat .env

# View logs
# (logs appear in terminal where backend is running)

# Install dependencies
cd backend
venv311/Scripts/pip install -r requirements.txt
```

### Frontend
```bash
# Start dev server
cd frontend
npm run dev

# Install dependencies
cd frontend
npm install

# Build for production
npm run build
```

### Git
```bash
# Check status
git status

# Commit changes
git add .
git commit -m "Your message"

# Push to GitHub
git push
```

---

## Performance

### Expected Processing Times
- **OCR:** 20-30 seconds
- **Script Generation:** 30-60 seconds
- **TTS Audio:** 60-90 seconds
- **Total:** 2-3 minutes per upload

### Optimizations
- Background task processing (non-blocking)
- Efficient file handling
- Cached static files
- Hot module reloading in dev

---

## Security Notes

1. **API Key:** Keep `.env` file private
2. **File Upload:** Validates file types (jpg, png, pdf)
3. **CORS:** Currently allows all origins (restrict in production)
4. **File Storage:** Local storage only (consider cloud for production)

---

## Support

For issues or questions:
1. Check `backend/backups/README.md` for detailed troubleshooting
2. Review backend logs in terminal
3. Use emergency restore if needed

---

**Last Updated:** December 12, 2024
**Version:** 1.0 (Stable)
**Status:** ✅ Fully Working
