"""
Script Generator Service with Retry Logic
Handles Gemini API overload (503 errors)
"""

import os
import httpx
import asyncio
import random

from dotenv import load_dotenv
load_dotenv()


class ScriptGenerator:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

        if self.api_key:
            print(f"[SCRIPT] API key loaded: {self.api_key[:15]}...")
        else:
            print("[SCRIPT] WARNING: No API key found!")

    async def generate_script(self, extracted_text: str, subject: str = "General", chapter: str = "Notes") -> str:
        """Generate Hinglish podcast script with retry logic"""
        print(f"[SCRIPT] Generating script for {subject} - {chapter}")
        print(f"[SCRIPT] Input text length: {len(extracted_text)} chars")

        if not self.api_key:
            return self._get_demo_script(subject, chapter)

        prompt = self._create_prompt(extracted_text, subject, chapter)

        # Retry up to 3 times with exponential backoff
        max_retries = 3

        for attempt in range(max_retries):
            try:
                script = await self._call_api(prompt, attempt)
                if script:
                    print(f"[SCRIPT] SUCCESS! Generated {len(script)} chars")
                    return script

            except Exception as e:
                print(f"[SCRIPT] Attempt {attempt + 1} failed: {e}")

                if attempt < max_retries - 1:
                    # Exponential backoff: 2s, 4s, 8s
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"[SCRIPT] Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)

        # All retries failed - return demo script
        print("[SCRIPT] All retries failed, using demo script")
        return self._get_demo_script(subject, chapter)

    async def _call_api(self, prompt: str, attempt: int = 0) -> str:
        """Make API call to Gemini"""

        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.8,
                "maxOutputTokens": 8192
            }
        }

        url = f"{self.api_url}?key={self.api_key}"

        # Increase timeout for retries
        timeout = 60 + (attempt * 30)

        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=payload)

            print(f"[SCRIPT] API Response Status: {response.status_code}")

            # Handle 503 - Model Overloaded
            if response.status_code == 503:
                error_data = response.json() if response.text else {}
                print(f"[SCRIPT] Model overloaded (503): {error_data}")
                raise Exception("Model overloaded - will retry")

            # Handle other errors
            if response.status_code != 200:
                print(f"[SCRIPT] API Error: {response.text[:300]}")
                raise Exception(f"API error {response.status_code}")

            result = response.json()

            if "candidates" in result and len(result["candidates"]) > 0:
                content = result["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    return parts[0].get("text", "")

            raise Exception("No content in response")

    def _create_prompt(self, text: str, subject: str, chapter: str) -> str:
        """Create the podcast script generation prompt"""

        return f"""You are a scriptwriter for an educational podcast called "SaarLM" targeted at Indian JEE/NEET students.

Create an engaging Hinglish (Hindi + English mix) podcast script based on the following study notes.

CHARACTERS:
- DIDI: A warm, encouraging female tutor who explains concepts clearly
- BHAIYA: An energetic male tutor who adds exam tips and memory tricks

RULES:
1. Write in Hinglish (mix Hindi and English naturally, like Indian students speak)
2. Start with a warm greeting from DIDI
3. Alternate between DIDI and BHAIYA
4. DIDI explains the main concepts
5. BHAIYA adds shortcuts, mnemonics, and exam tips
6. Include "Toh yaad rakhna!" moments for key points
7. End with a motivational closing
8. Keep it conversational and fun, not boring!
9. Use relatable examples from daily Indian life

SUBJECT: {subject}
CHAPTER: {chapter}

STUDY NOTES:
{text[:4000]}

FORMAT YOUR RESPONSE EXACTLY LIKE THIS:
DIDI: [dialogue]
BHAIYA: [dialogue]
DIDI: [dialogue]
...

Generate an engaging 5-7 minute podcast script now:"""

    def _get_demo_script(self, subject: str, chapter: str) -> str:
        """Fallback demo script when API fails"""

        return f"""DIDI: Hello hello, mere pyaare students! Main hoon aapki Didi, aur aaj hum {subject} ke ek important topic pe baat karenge!

BHAIYA: Aur main hoon Bhaiya! Aaj ka topic hai {chapter}. Didi, shuru karein?

DIDI: Haan Bhaiya! Toh dekho beta, yeh topic bahut important hai exam ke liye. Basic concepts se shuru karte hain.

BHAIYA: Ek important tip yaad rakhna - jab bhi yeh topic aaye, pehle fundamentals clear karo!

DIDI: Bilkul sahi Bhaiya! Toh students, is topic mein humne key points cover kiye. Practice karte raho!

BHAIYA: Aur haan, revision mat bhoolna! Daily 15 minutes is topic ko do.

DIDI: Sahi baat hai! Toh aaj ke liye itna hi. Keep studying, keep shining!

BHAIYA: All the best for your exams! Jai Hind!"""
