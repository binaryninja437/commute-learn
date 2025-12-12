"""
OCR Service - Google Gemini Vision API
Fresh clean version - Dec 2024
"""

import os
import base64
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OCRService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        print(f"[OCR] Initialized")
        print(f"[OCR] API Key present: {bool(self.api_key)}")
        if self.api_key:
            print(f"[OCR] API Key starts with: {self.api_key[:10]}...")

    async def extract_text(self, file_path: str) -> str:
        print(f"\n[OCR] ========== EXTRACT TEXT ==========")
        print(f"[OCR] File: {file_path}")

        # Check API key
        if not self.api_key:
            print("[OCR] ERROR: No API key!")
            return "Error: No GEMINI_API_KEY in .env file"

        # Read file
        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
            print(f"[OCR] File size: {len(file_bytes)} bytes")
        except Exception as e:
            print(f"[OCR] ERROR reading file: {e}")
            return f"Error reading file: {e}"

        # Determine file type
        ext = file_path.split(".")[-1].lower()
        print(f"[OCR] File extension: {ext}")

        if ext in ["jpg", "jpeg", "png", "webp"]:
            return await self._ocr_image(file_bytes, ext)
        elif ext == "pdf":
            return await self._ocr_pdf(file_path)
        else:
            return f"Unsupported file type: {ext}"

    async def _ocr_image(self, image_bytes: bytes, ext: str) -> str:
        print(f"[OCR] Processing image...")

        # Convert to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        print(f"[OCR] Base64 length: {len(image_b64)}")

        # Determine MIME type
        mime_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        mime_type = mime_map.get(ext, "image/jpeg")
        print(f"[OCR] MIME type: {mime_type}")

        # Build API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={self.api_key}"

        payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract ALL text from this image exactly as written. Include headings, bullet points, formulas, equations. Return ONLY the extracted text."},
                    {"inline_data": {"mime_type": mime_type, "data": image_b64}}
                ]
            }],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}
        }

        # Make API call
        print(f"[OCR] Calling Gemini API...")
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)

            print(f"[OCR] Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[OCR] SUCCESS! Extracted {len(text)} chars")
                try:
                    print(f"[OCR] Preview: {text[:200]}...")
                except:
                    print(f"[OCR] Preview: (contains special characters)")
                return text
            else:
                error_text = response.text[:500]
                print(f"[OCR] API ERROR: {error_text}")
                return f"API Error {response.status_code}: {error_text}"

        except Exception as e:
            print(f"[OCR] EXCEPTION: {e}")
            return f"OCR Exception: {e}"

    async def _ocr_pdf(self, pdf_path: str) -> str:
        print(f"[OCR] Processing PDF...")
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"Page {i+1}:\n{page_text}\n\n"
            print(f"[OCR] PDF extracted: {len(text)} chars")
            return text if text.strip() else "PDF has no extractable text. Please upload as image."
        except Exception as e:
            print(f"[OCR] PDF ERROR: {e}")
            return f"PDF Error: {e}"
