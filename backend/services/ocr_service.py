"""
OCR Service - Working Version
"""

import os
import base64
import httpx

from dotenv import load_dotenv
load_dotenv()


class OCRService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        print(f"[OCR INIT] API Key: {'LOADED - ' + self.api_key[:15] + '...' if self.api_key else 'NOT FOUND'}")

    async def extract_text(self, file_path: str) -> str:
        file_extension = file_path.split(".")[-1].lower()
        print(f"[OCR] Processing: {file_path} (type: {file_extension})")

        if file_extension in ["jpg", "jpeg", "png", "webp"]:
            return await self._extract_from_image(file_path)
        elif file_extension == "pdf":
            return await self._extract_from_pdf(file_path)
        else:
            return f"Unsupported file type: {file_extension}"

    async def _extract_from_image(self, image_path: str) -> str:
        print(f"[OCR] Reading image file...")

        # Read the image file
        try:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
            print(f"[OCR] Image loaded: {len(image_bytes)} bytes")
        except Exception as e:
            print(f"[OCR] Failed to read file: {e}")
            return f"Error reading file: {e}"

        # Check API key
        if not self.api_key:
            print("[OCR] No API key!")
            return "ERROR: No API key configured. Check .env file."

        # Encode to base64
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        # Detect mime type
        mime_type = "image/jpeg"
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            mime_type = "image/png"
        print(f"[OCR] MIME: {mime_type}")

        # Call Gemini API
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract ALL text from this image exactly as written. Include headings, bullet points, formulas. Return ONLY the text."},
                    {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                ]
            }],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 8192}
        }

        try:
            print("[OCR] Calling Gemini Vision API...")
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.api_url}?key={self.api_key}",
                    json=payload
                )

            print(f"[OCR] Response: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[OCR] SUCCESS! Got {len(text)} characters")
                # Don't print preview - may contain special chars that Windows console can't handle
                return text
            else:
                print(f"[OCR] API Error: {response.text[:300]}")
                return f"API Error: {response.status_code}"

        except Exception as e:
            print(f"[OCR] Exception: {e}")
            return f"OCR Exception: {e}"

    async def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pypdf"""
        try:
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            text = ""

            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"--- Page {i+1} ---\n{page_text}\n\n"

            print(f"[OCR] PDF extracted: {len(text)} characters")

            if len(text.strip()) > 30:
                return text

            # If no text extracted, PDF might be scanned - return message
            return "PDF appears to be scanned/image-based. Please upload as image (JPG/PNG) for OCR."

        except Exception as e:
            print(f"[OCR] PDF error: {e}")
            return f"PDF extraction failed: {e}"
