"""
Commute & Learn - Backend API
India's #1 Audio Study App for JEE/NEET Students
Converts PDFs/Notes → Hinglish Audio Podcasts
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env file FIRST before any other imports

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional
import json

from services.ocr_service import OCRService
from services.script_generator import ScriptGenerator
from services.tts_service import TTSService
from models.schemas import (
    ProcessingStatus, 
    PodcastResponse, 
    ProcessingRequest,
    PodcastMetadata
)

# Initialize FastAPI app
app = FastAPI(
    title="Commute & Learn API",
    description="Convert study materials to Hinglish audio podcasts",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for uploads and generated content
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
METADATA_DIR = "metadata"

for dir_path in [UPLOAD_DIR, OUTPUT_DIR, METADATA_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Mount static files for serving audio
app.mount("/audio", StaticFiles(directory=OUTPUT_DIR), name="audio")

# In-memory job status tracking (use Redis in production)
job_status = {}

# Initialize services
ocr_service = OCRService()
script_generator = ScriptGenerator()
tts_service = TTSService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "app": "Commute & Learn",
        "version": "1.0.0",
        "message": "Padhai ka naya tareeka! 📚🎧"
    }


@app.post("/api/upload")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    subject: Optional[str] = "General",
    chapter: Optional[str] = "Notes"
):
    """
    Upload a PDF or image file for processing
    Returns a job_id for tracking progress
    """
    # Validate file type
    allowed_types = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/webp"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Use PDF or images."
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())[:8]
    
    # Save uploaded file
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "pdf"
    saved_filename = f"{job_id}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, saved_filename)
    
    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Initialize job status
    job_status[job_id] = {
        "status": "uploaded",
        "progress": 10,
        "message": "File uploaded successfully! ✅",
        "stage": "upload",
        "file_path": file_path,
        "subject": subject,
        "chapter": chapter,
        "original_filename": file.filename,
        "created_at": datetime.now().isoformat()
    }
    
    # Start background processing
    background_tasks.add_task(process_file, job_id)
    
    return {
        "job_id": job_id,
        "status": "processing",
        "message": "File uploaded! Processing shuru ho gaya hai... 🚀"
    }


async def process_file(job_id: str):
    """
    Background task to process uploaded file through the AI pipeline:
    1. OCR (Extract text from PDF/Image)
    2. Summarize & Generate Script (Didi + Bhaiya dialogue)
    3. TTS (Convert script to audio)
    """
    try:
        job = job_status[job_id]
        file_path = job["file_path"]
        
        # Stage 1: OCR - Extract text
        job_status[job_id].update({
            "status": "processing",
            "progress": 20,
            "message": "📖 Text nikal rahe hain...",
            "stage": "ocr"
        })
        
        extracted_text = await ocr_service.extract_text(file_path)

        print(f"[DEBUG] Extracted text length: {len(extracted_text) if extracted_text else 0}")
        print(f"[DEBUG] Extracted text preview: {extracted_text[:200] if extracted_text else 'NONE'}...")

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise Exception("Could not extract enough text from the file. Please ensure the image/PDF contains readable text.")
        
        job_status[job_id].update({
            "progress": 40,
            "message": "✅ Text mil gaya! Script likh rahe hain...",
            "stage": "script",
            "extracted_length": len(extracted_text)
        })
        
        # Stage 2: Generate Hinglish Script
        script = await script_generator.generate_script(
            extracted_text=extracted_text,
            subject=job["subject"],
            chapter=job["chapter"]
        )
        
        job_status[job_id].update({
            "progress": 60,
            "message": "📝 Script ready! Audio bana rahe hain...",
            "stage": "tts",
            "script_preview": script[:200] + "..."
        })
        
        # Stage 3: Text-to-Speech
        audio_filename = f"{job_id}_podcast.mp3"
        audio_path = os.path.join(OUTPUT_DIR, audio_filename)
        
        duration = await tts_service.generate_audio(script, audio_path)
        
        # Save metadata
        metadata = {
            "job_id": job_id,
            "title": f"{job['subject']} - {job['chapter']}",
            "original_file": job["original_filename"],
            "duration": duration,
            "created_at": job["created_at"],
            "audio_file": audio_filename,
            "script": script
        }
        
        metadata_path = os.path.join(METADATA_DIR, f"{job_id}.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        # Mark as complete
        job_status[job_id].update({
            "status": "completed",
            "progress": 100,
            "message": "🎉 Podcast ready! Sunne ka time!",
            "stage": "done",
            "audio_url": f"/audio/{audio_filename}",
            "duration": duration,
            "metadata": metadata
        })
        
    except Exception as e:
        job_status[job_id].update({
            "status": "failed",
            "progress": 0,
            "message": f"❌ Error: {str(e)}",
            "stage": "error",
            "error": str(e)
        })


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get processing status for a job"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status[job_id]


@app.get("/api/download/{job_id}")
async def download_audio(job_id: str):
    """Download the generated podcast MP3"""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = job_status[job_id]
    
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Podcast not ready yet")
    
    audio_filename = f"{job_id}_podcast.mp3"
    audio_path = os.path.join(OUTPUT_DIR, audio_filename)
    
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename=f"commute_learn_{job['subject']}_{job['chapter']}.mp3"
    )


@app.get("/api/library")
async def get_library():
    """Get all generated podcasts (user's library)"""
    podcasts = []
    
    for filename in os.listdir(METADATA_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(METADATA_DIR, filename), "r", encoding="utf-8") as f:
                metadata = json.load(f)
                podcasts.append(metadata)
    
    # Sort by creation date (newest first)
    podcasts.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return {"podcasts": podcasts, "total": len(podcasts)}


@app.delete("/api/podcast/{job_id}")
async def delete_podcast(job_id: str):
    """Delete a podcast from the library"""
    metadata_path = os.path.join(METADATA_DIR, f"{job_id}.json")
    audio_path = os.path.join(OUTPUT_DIR, f"{job_id}_podcast.mp3")
    
    deleted = False
    
    if os.path.exists(metadata_path):
        os.remove(metadata_path)
        deleted = True
    
    if os.path.exists(audio_path):
        os.remove(audio_path)
        deleted = True
    
    if job_id in job_status:
        del job_status[job_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Podcast not found")
    
    return {"message": "Podcast deleted successfully"}


# Demo endpoint for testing without actual AI
@app.post("/api/demo")
async def create_demo_podcast():
    """Create a demo podcast for testing the UI"""
    job_id = "demo_" + str(uuid.uuid4())[:4]

    # Simulate processing stages
    job_status[job_id] = {
        "status": "completed",
        "progress": 100,
        "message": "🎉 Demo podcast ready!",
        "stage": "done",
        "audio_url": "/audio/demo.mp3",
        "duration": 180,
        "metadata": {
            "job_id": job_id,
            "title": "Physics - Newton's Laws (Demo)",
            "duration": 180,
            "created_at": datetime.now().isoformat()
        }
    }

    return job_status[job_id]


@app.get("/api/test-gemini")
async def test_gemini():
    """Test endpoint to verify Gemini API key is working"""
    import httpx

    api_key = os.getenv("GEMINI_API_KEY", "")

    print(f"\n🔍 TEST: API Key present: {bool(api_key)}")
    if api_key:
        print(f"🔍 TEST: API Key starts with: {api_key[:15]}...")

    if not api_key:
        return {"error": "No API key found in environment variables"}

    # Test with the correct model name
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    payload = {
        "contents": [{"parts": [{"text": "Say hello in Hindi"}]}]
    }

    print(f"🔍 TEST: Testing Gemini API at: {url[:80]}...")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

            print(f"🔍 TEST: Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"✅ TEST: Gemini API working!")
                return {
                    "status": "success",
                    "status_code": response.status_code,
                    "response": result
                }
            else:
                print(f"❌ TEST: Gemini API error: {response.text[:200]}")
                return {
                    "status": "error",
                    "status_code": response.status_code,
                    "error": response.text
                }
    except Exception as e:
        print(f"❌ TEST: Exception: {str(e)}")
        return {
            "status": "exception",
            "error": str(e)
        }


@app.get("/api/test-ocr")
async def test_ocr():
    """Test if OCR and API key are working"""
    import os
    import httpx
    import base64

    results = {
        "step1_env_key": None,
        "step2_api_test": None,
        "step3_vision_test": None
    }

    # Step 1: Check if API key is loaded
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        results["step1_env_key"] = "FAILED - No API key in environment"
        return results
    results["step1_env_key"] = f"PASSED - Key starts with: {api_key[:15]}..."

    # Step 2: Test basic API call
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": "Say hello"}]}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            results["step2_api_test"] = f"PASSED - Status {response.status_code}"
        else:
            results["step2_api_test"] = f"FAILED - Status {response.status_code}: {response.text[:200]}"
            return results
    except Exception as e:
        results["step2_api_test"] = f"FAILED - Exception: {str(e)}"
        return results

    # Step 3: Test Vision API with a simple test image
    try:
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [
                    {"text": "What color is this image? Reply in one word."},
                    {"inline_data": {"mime_type": "image/png", "data": test_image_b64}}
                ]
            }]
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload)

        if response.status_code == 200:
            result = response.json()
            text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            results["step3_vision_test"] = f"PASSED - Vision works! Response: {text[:50]}"
        else:
            results["step3_vision_test"] = f"FAILED - Status {response.status_code}: {response.text[:200]}"
    except Exception as e:
        results["step3_vision_test"] = f"FAILED - Exception: {str(e)}"

    return results


@app.post("/api/debug-upload")
async def debug_upload(file: UploadFile = File(...)):
    """Debug endpoint - shows exactly what happens at each step"""
    import os
    import base64
    import httpx

    results = {
        "step1_file_received": None,
        "step2_file_saved": None,
        "step3_file_read": None,
        "step4_api_call": None,
        "step5_extracted_text": None,
    }

    # Step 1: File received
    results["step1_file_received"] = f"OK - Filename: {file.filename}, Type: {file.content_type}"

    # Step 2: Save file temporarily
    temp_path = f"debug_test_{file.filename}"
    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)
        results["step2_file_saved"] = f"OK - Saved {len(content)} bytes to {temp_path}"
    except Exception as e:
        results["step2_file_saved"] = f"FAILED - {e}"
        return results

    # Step 3: Read and encode
    try:
        with open(temp_path, "rb") as f:
            image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        mime_type = "image/jpeg"
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            mime_type = "image/png"

        results["step3_file_read"] = f"OK - {len(image_bytes)} bytes, MIME: {mime_type}, Base64: {len(image_base64)} chars"
    except Exception as e:
        results["step3_file_read"] = f"FAILED - {e}"
        return results

    # Step 4: Call Gemini API directly
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        results["step4_api_call"] = "FAILED - No API key"
        return results

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

        payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract ALL text from this image exactly as written. Return ONLY the extracted text."},
                    {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                ]
            }]
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)

        results["step4_api_call"] = f"Status: {response.status_code}"

        if response.status_code == 200:
            result = response.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            results["step5_extracted_text"] = f"SUCCESS - {len(text)} chars: {text[:500]}..."
        else:
            results["step5_extracted_text"] = f"FAILED - API returned: {response.text[:500]}"

    except Exception as e:
        results["step4_api_call"] = f"FAILED - Exception: {e}"

    # Cleanup
    try:
        os.remove(temp_path)
    except:
        pass

    return results


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
