"""
SaarLM Backend - Complete Working Version
"""

import os
import sys
import io
import json
import uuid
import base64
from datetime import datetime
from typing import Optional
import asyncio

# Fix Windows UTF-8 encoding FIRST
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from fastapi import FastAPI, File, UploadFile, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
from dotenv import load_dotenv

# Load environment variables FIRST
load_dotenv()

# Get API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
print(f"\n{'='*60}")
print(f"[STARTUP] SaarLM Backend Starting...")
print(f"[STARTUP] API Key: {'LOADED - ' + GEMINI_API_KEY[:15] + '...' if GEMINI_API_KEY else 'MISSING!'}")
print(f"{'='*60}\n")

# Create FastAPI app
app = FastAPI(title="SaarLM API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
METADATA_DIR = "metadata"

for d in [UPLOAD_DIR, OUTPUT_DIR, METADATA_DIR]:
    os.makedirs(d, exist_ok=True)

# Job storage
jobs = {}

# Mount static files
app.mount("/audio", StaticFiles(directory=OUTPUT_DIR), name="audio")


@app.get("/")
async def root():
    return {
        "status": "online",
        "app": "SaarLM",
        "version": "1.0.0",
        "api_key_loaded": bool(GEMINI_API_KEY)
    }


@app.post("/api/test-ocr")
async def test_ocr():
    """Test if API key works"""
    if not GEMINI_API_KEY:
        return {"error": "No API key"}

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": "Say hello"}]}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

        return {"status": response.status_code, "works": response.status_code == 200}
    except Exception as e:
        return {"error": str(e)}


@app.post("/api/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject: str = Form("General"),
    chapter: str = Form("Notes")
):
    """Upload file and start processing"""
    print(f"\n{'='*60}")
    print(f"[UPLOAD] New file: {file.filename}")
    print(f"[UPLOAD] Subject: {subject}, Chapter: {chapter}")
    print(f"{'='*60}")

    # Generate job ID
    job_id = str(uuid.uuid4())[:8]

    # Save file
    ext = file.filename.split(".")[-1].lower()
    file_path = os.path.join(UPLOAD_DIR, f"{job_id}.{ext}")

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    print(f"[UPLOAD] Saved: {file_path} ({len(content)} bytes)")

    # Initialize job
    jobs[job_id] = {"status": "processing", "progress": 0, "stage": "upload"}

    # Start processing in background
    background_tasks.add_task(process_file_direct, job_id, file_path, subject, chapter)

    return {"job_id": job_id, "status": "processing"}


async def process_file_direct(job_id: str, file_path: str, subject: str, chapter: str):
    """Process file - ALL IN ONE FUNCTION (no service classes)"""
    try:
        print(f"\n{'='*60}")
        print(f"[PROCESS] Job {job_id} starting...")
        print(f"[PROCESS] API Key: {GEMINI_API_KEY[:15] if GEMINI_API_KEY else 'MISSING'}...")
        print(f"{'='*60}")

        # ============ STEP 1: OCR ============
        print(f"\n[STEP 1] OCR - Reading image...")
        jobs[job_id] = {"status": "processing", "progress": 20, "stage": "ocr"}

        with open(file_path, "rb") as f:
            image_bytes = f.read()

        image_b64 = base64.b64encode(image_bytes).decode("utf-8")

        ext = file_path.split(".")[-1].lower()
        mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

        ocr_payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract ALL text from this image exactly as written. Include all headings, bullet points, formulas. Return ONLY the extracted text."},
                    {"inline_data": {"mime_type": mime_type, "data": image_b64}}
                ]
            }],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}
        }

        print(f"[STEP 1] Calling Gemini Vision API...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=ocr_payload)

        print(f"[STEP 1] Response: {response.status_code}")

        if response.status_code != 200:
            print(f"[STEP 1] ERROR: {response.text[:300]}")
            jobs[job_id] = {"status": "error", "error": f"OCR failed: {response.status_code}"}
            return

        result = response.json()
        extracted_text = result["candidates"][0]["content"]["parts"][0]["text"]
        print(f"[STEP 1] SUCCESS! Extracted {len(extracted_text)} chars")
        print(f"[STEP 1] Preview: {extracted_text[:200]}...")

        # ============ STEP 2: SCRIPT GENERATION ============
        print(f"\n[STEP 2] Generating podcast script...")
        jobs[job_id] = {"status": "processing", "progress": 50, "stage": "script"}

        script_prompt = f"""Create a Hinglish podcast script for Indian JEE/NEET students.

CHARACTERS:
- DIDI: Female tutor, warm and encouraging
- BHAIYA: Male tutor, gives exam tips

STRICT RULES - MUST FOLLOW:
1. Use Hinglish (Hindi + English mix)
2. Base content ONLY on the notes provided below
3. Make it conversational and engaging
4. 5-8 minutes long

⚠️ CRITICAL - DO NOT INCLUDE:
- NO phone numbers (real or fake)
- NO WhatsApp numbers
- NO email addresses
- NO website URLs
- NO social media handles
- NO contact information of any kind
- NO promotional content
- NO references to external services
- NO made-up statistics or data not in the notes

ONLY discuss the educational content from the notes. End with motivation like "Keep studying!" or "All the best!" but NO contact details.

SUBJECT: {subject}
CHAPTER: {chapter}

STUDY NOTES:
{extracted_text[:3500]}

FORMAT:
DIDI: [dialogue]
BHAIYA: [dialogue]

Generate the complete podcast script (educational content only, no contact info):"""

        script_payload = {
            "contents": [{"parts": [{"text": script_prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
        }

        print(f"[STEP 2] Calling Gemini API for script...")
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(url, json=script_payload)

        print(f"[STEP 2] Response: {response.status_code}")

        if response.status_code != 200:
            print(f"[STEP 2] ERROR: {response.text[:300]}")
            jobs[job_id] = {"status": "error", "error": f"Script failed: {response.status_code}"}
            return

        result = response.json()
        script = result["candidates"][0]["content"]["parts"][0]["text"]
        print(f"[STEP 2] Generated {len(script)} chars")

        # ============ SAFETY FILTER ============
        import re

        # Remove phone numbers (Indian format)
        script = re.sub(r'\b\d{10}\b', '', script)
        script = re.sub(r'\b\d{5}[\s-]?\d{5}\b', '', script)
        script = re.sub(r'\+91[\s-]?\d{10}', '', script)

        # Remove WhatsApp references with numbers
        script = re.sub(r'[Ww]hats[Aa]pp[^\n]*\d+[^\n]*', '', script)
        script = re.sub(r'[Cc]ontact[^\n]*\d+[^\n]*', '', script)
        script = re.sub(r'[Cc]all[^\n]*\d+[^\n]*', '', script)

        # Remove email addresses
        script = re.sub(r'\b[\w.-]+@[\w.-]+\.\w+\b', '', script)

        # Remove URLs
        script = re.sub(r'https?://\S+', '', script)
        script = re.sub(r'www\.\S+', '', script)

        # Clean up empty lines
        script = re.sub(r'\n\s*\n\s*\n', '\n\n', script)

        print(f"[STEP 2] After safety filter: {len(script)} chars")
        print(f"[STEP 2] Preview: {script[:200]}...")

        # ============ STEP 3: TTS ============
        print(f"\n[STEP 3] Generating audio...")
        jobs[job_id] = {"status": "processing", "progress": 75, "stage": "tts"}

        from services.tts_service import TTSService
        tts = TTSService()

        audio_filename = f"{job_id}.mp3"
        audio_path = os.path.join(OUTPUT_DIR, audio_filename)

        duration = await tts.generate_audio(script, audio_path)
        print(f"[STEP 3] SUCCESS! Audio duration: {duration}s")

        # ============ STEP 4: SAVE METADATA ============
        print(f"\n[STEP 4] Saving metadata...")

        metadata = {
            "job_id": job_id,
            "title": f"{subject} - {chapter}",
            "subject": subject,
            "chapter": chapter,
            "duration": duration,
            "audio_file": audio_filename,
            "script": script,
            "extracted_text": extracted_text[:1000],
            "created_at": datetime.now().isoformat()
        }

        metadata_path = os.path.join(METADATA_DIR, f"{job_id}.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

        # ============ COMPLETE ============
        print(f"\n{'='*60}")
        print(f"[COMPLETE] Job {job_id} finished successfully!")
        print(f"{'='*60}\n")

        jobs[job_id] = {
            "status": "completed",
            "progress": 100,
            "stage": "done",
            "audio_url": f"/audio/{audio_filename}",
            "duration": duration,
            "script": script,
            "metadata": {
                "job_id": job_id,
                "title": f"{subject} - {chapter}",
                "subject": subject,
                "chapter": chapter,
                "duration": duration,
                "audio_file": audio_filename,
                "created_at": datetime.now().isoformat()
            }
        }

    except Exception as e:
        print(f"\n[ERROR] Job {job_id} failed: {e}")
        import traceback
        traceback.print_exc()
        jobs[job_id] = {"status": "error", "error": str(e)}


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]


@app.get("/api/library")
async def get_library():
    """Get all podcasts"""
    podcasts = []
    for filename in os.listdir(METADATA_DIR):
        if filename.endswith(".json"):
            try:
                with open(os.path.join(METADATA_DIR, filename), "r", encoding="utf-8") as f:
                    podcasts.append(json.load(f))
            except Exception as e:
                print(f"[LIBRARY] Error loading {filename}: {e}")
                continue

    podcasts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"podcasts": podcasts, "total": len(podcasts)}


@app.get("/api/podcast/{job_id}")
async def get_podcast(job_id: str):
    """Get single podcast"""
    metadata_path = os.path.join(METADATA_DIR, f"{job_id}.json")
    if not os.path.exists(metadata_path):
        raise HTTPException(status_code=404, detail="Podcast not found")

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


@app.delete("/api/podcast/{job_id}")
async def delete_podcast(job_id: str):
    """Delete podcast"""
    metadata_path = os.path.join(METADATA_DIR, f"{job_id}.json")
    audio_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp3")

    if os.path.exists(metadata_path):
        os.remove(metadata_path)
    if os.path.exists(audio_path):
        os.remove(audio_path)

    return {"status": "deleted"}


@app.get("/api/download/{job_id}")
async def download_audio(job_id: str):
    """Download audio file"""
    audio_path = os.path.join(OUTPUT_DIR, f"{job_id}.mp3")
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio not found")

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"saarlm-{job_id}.mp3"
    )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
