# 🔒 SaarLM Backup Files

This folder contains tested, working versions of critical files.

## Current Configuration

**Backend:** Port 8001 (with PYTHONIOENCODING=utf-8)
**Frontend:** Port 3002
**API Key:** Working Gemini 2.5 Flash key loaded
**Date:** December 12, 2024

## How to Restore

If something breaks, copy the backup file to replace the broken one:

### On Linux/Mac:
```bash
# Restore main.py
cp backend/backups/main_working_v1.py backend/main.py

# Restore all services
cp backend/backups/ocr_service_working_v1.py backend/services/ocr_service.py
cp backend/backups/script_generator_working_v1.py backend/services/script_generator.py
cp backend/backups/tts_service_working_v1.py backend/services/tts_service.py
```

### On Windows:
```cmd
REM Restore main.py
copy backend\backups\main_working_v1.py backend\main.py

REM Restore all services
copy backend\backups\ocr_service_working_v1.py backend\services\ocr_service.py
copy backend\backups\script_generator_working_v1.py backend\services\script_generator.py
copy backend\backups\tts_service_working_v1.py backend\services\tts_service.py
```

### Quick Restore Script:
- **Windows:** Double-click `restore.bat`
- **Linux/Mac:** Run `bash restore.sh`

Then restart the backend:
```bash
cd backend
set PYTHONIOENCODING=utf-8
"venv311/Scripts/python.exe" -m uvicorn main:app --reload --port 8001
```

## Backup History

| File | Version | Date | Status | Notes |
|------|---------|------|--------|-------|
| main_working_v1.py | 1.0 | Dec 12 2024 | ✅ Tested | UTF-8 encoding, status fix, all-in-one processing |
| ocr_service_working_v1.py | 1.0 | Dec 12 2024 | ✅ Tested | Gemini Vision API with proper encoding |
| script_generator_working_v1.py | 1.0 | Dec 12 2024 | ✅ Tested | Hinglish script generation |
| tts_service_working_v1.py | 1.0 | Dec 12 2024 | ✅ Tested | Multi-voice gTTS with pydub |
| App_working_v1.jsx | 1.0 | Dec 12 2024 | ✅ Tested | Frontend with dual status support |

## Key Features in This Backup

### Backend (main.py v1.0)
- ✅ UTF-8 encoding wrapper for Windows
- ✅ All-in-one processing (no external service classes)
- ✅ Gemini 2.5 Flash API integration
- ✅ Status returns both "complete" and "completed"
- ✅ Proper error handling with UTF-8 file reading
- ✅ Background task processing
- ✅ Static file serving for audio
- ✅ Library/metadata endpoints with encoding safety

### Frontend (App.jsx v1.0)
- ✅ Accepts both "complete" and "completed" status
- ✅ Proper script and metadata display
- ✅ Spotify-like UI with Tailwind CSS
- ✅ Audio player with progress bar
- ✅ Library view with all podcasts
- ✅ Upload with drag-and-drop

### Services (OCR/Script/TTS)
- ✅ Gemini Vision API for OCR
- ✅ Hinglish podcast script generation
- ✅ Multi-voice TTS (male/female alternating)
- ✅ Error handling and fallback scripts
- ✅ Proper Unicode handling

## Common Issues & Solutions

### Issue 1: "Internal Server Error" on /api/library
**Cause:** Unicode characters in metadata files
**Solution:** Backend must run with `PYTHONIOENCODING=utf-8`

### Issue 2: Podcast not loading after upload
**Cause:** Status mismatch ("complete" vs "completed")
**Solution:** Frontend now accepts both status strings

### Issue 3: OCR not extracting text
**Cause:** Gemini API quota exhausted
**Solution:** Update API key in `.env` file

### Issue 4: 'charmap' codec errors
**Cause:** Windows default encoding (cp1252)
**Solution:** UTF-8 wrapper in main.py + PYTHONIOENCODING env var

## Environment Variables (.env)

```env
GEMINI_API_KEY=AIzaSyCAihYrPAf7eGfyqveAFOE-XQwPnUAk2-k
PORT=8001
```

## Testing Checklist

Before creating a backup, verify:
- [ ] Backend starts without errors
- [ ] Frontend loads at http://localhost:3002
- [ ] Upload works (file accepted)
- [ ] OCR extracts text from image
- [ ] Script generated in Hinglish
- [ ] Audio file created
- [ ] Podcast displays in player
- [ ] Library shows all podcasts
- [ ] Download audio works

## Last Tested: December 12, 2024 ✅

All features working with:
- Sample upload: GRAVITATION notes (Physics)
- OCR: Successfully extracted formulas with subscripts (m₁, m₂, r²)
- Script: Full Hinglish podcast with Didi & Bhaiya characters
- Audio: 513 seconds duration
- Status: Proper transition to player view
