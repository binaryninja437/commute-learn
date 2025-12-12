"""
Script Generator - Google Gemini API
Fresh clean version - Dec 2024
"""

import os
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScriptGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        print(f"[SCRIPT] Initialized")
        print(f"[SCRIPT] API Key present: {bool(self.api_key)}")
        if self.api_key:
            print(f"[SCRIPT] API Key starts with: {self.api_key[:10]}...")

    async def generate_script(self, text: str, subject: str = "General", chapter: str = "Notes") -> str:
        print(f"\n[SCRIPT] ========== GENERATE SCRIPT ==========")
        print(f"[SCRIPT] Subject: {subject}, Chapter: {chapter}")
        print(f"[SCRIPT] Input text length: {len(text)} chars")
        try:
            print(f"[SCRIPT] Input preview: {text[:200]}...")
        except:
            print(f"[SCRIPT] Input preview: <contains special characters>")

        # Check API key
        if not self.api_key:
            print("[SCRIPT] ERROR: No API key!")
            return self._fallback_script(subject, chapter)

        # Check input text
        if not text or len(text.strip()) < 20:
            print("[SCRIPT] ERROR: Input text too short!")
            return self._fallback_script(subject, chapter)

        # Build prompt
        prompt = f"""Create a Hinglish podcast script for Indian JEE/NEET students based on these notes.

CHARACTERS:
- DIDI: Female tutor, explains concepts warmly
- BHAIYA: Male tutor, gives exam tips and tricks

RULES:
1. Use Hinglish (Hindi + English mix)
2. DIDI explains concepts from the notes
3. BHAIYA adds exam tips
4. Make it engaging and conversational
5. 5-8 minutes long

SUBJECT: {subject}
CHAPTER: {chapter}

NOTES:
{text[:3500]}

FORMAT:
DIDI: [dialogue]
BHAIYA: [dialogue]

Generate the script now:"""

        # Build API request
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={self.api_key}"

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.8, "maxOutputTokens": 8192}
        }

        # Make API call
        print(f"[SCRIPT] Calling Gemini API...")
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(url, json=payload)

            print(f"[SCRIPT] Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"[SCRIPT] Full API response: {str(result)[:300]}")
                script = result["candidates"][0]["content"]["parts"][0]["text"]
                print(f"[SCRIPT] SUCCESS! Generated {len(script)} chars")
                try:
                    print(f"[SCRIPT] Preview: {script[:200]}...")
                except:
                    print(f"[SCRIPT] Preview: <contains special characters>")
                return script
            else:
                error_text = response.text[:500]
                print(f"[SCRIPT] API ERROR: {error_text}")
                return self._fallback_script(subject, chapter)

        except Exception as e:
            print(f"[SCRIPT] EXCEPTION: {e}")
            return self._fallback_script(subject, chapter)

    def _fallback_script(self, subject: str, chapter: str) -> str:
        print("[SCRIPT] Using fallback script")
        return f"""DIDI: Hello students! Aaj hum {subject} mein {chapter} padhenge!

BHAIYA: Haan Didi! Yeh topic bahut important hai exam ke liye.

DIDI: Toh shuru karte hain basic concepts se.

BHAIYA: Yaad rakhna - daily revision karo!

DIDI: All the best! Keep studying!

BHAIYA: Jai Hind!"""
