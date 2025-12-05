"""
Script Generator Service
Converts extracted text into engaging Hinglish podcast script
with two AI tutors: Didi (female) and Bhaiya (male)
"""

from dotenv import load_dotenv
load_dotenv()

import os
import httpx
import json
from typing import Optional


class ScriptGenerator:
    """
    Generates engaging podcast scripts in Hinglish
    Format: Two tutors (Didi & Bhaiya) discussing concepts
    """
    
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        
    async def generate_podcast_script(
        self,
        text: str,
        subject: str = "General",
        chapter: str = "Notes",
        duration_minutes: int = 10
    ) -> str:
        """
        Generate a Hinglish podcast script from extracted text
        """
        if not self.gemini_api_key:
            return self._get_demo_script(subject, chapter)
        
        try:
            prompt = self._create_prompt(text, subject, chapter, duration_minutes)
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.8,  # More creative
                    "maxOutputTokens": 8192,
                    "topP": 0.95
                }
            }
            
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.gemini_url}?key={self.gemini_api_key}",
                    json=payload
                )
                
                if response.status_code != 200:
                    import sys
                    sys.stderr.write(f"Script generation error: {response.status_code} - {response.text}\n")
                    sys.stderr.flush()
                    return self._get_demo_script(subject, chapter)
                
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0].get("content", {})
                    parts = content.get("parts", [])
                    if parts:
                        script = parts[0].get("text", "")
                        return self._clean_script(script)
                
                return self._get_demo_script(subject, chapter)
                
        except Exception as e:
            import sys
            sys.stderr.write(f"Script generation exception: {e}\n")
            sys.stderr.flush()
            return self._get_demo_script(subject, chapter)
    
    def _create_prompt(
        self,
        text: str,
        subject: str,
        chapter: str,
        duration_minutes: int
    ) -> str:
        """Create the prompt for script generation"""
        
        # Truncate text if too long (to fit in context)
        max_chars = 15000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n[... content truncated for length ...]"
        
        return f"""You are a script writer for "Commute & Learn" - India's #1 audio study app for JEE/NEET students.

Create an engaging {duration_minutes}-minute podcast script in HINGLISH (mix of Hindi and English) with TWO tutors:

**DIDI (Female tutor):**
- Friendly, encouraging, patient
- Explains "why" behind concepts
- Uses real-life analogies Indian students relate to
- Says things like "Dekho beta...", "Samjhe?", "Bilkul simple hai!"

**BHAIYA (Male tutor):**
- Energetic, exam-focused, practical
- Gives shortcuts, tricks, JEE/NEET tips
- Uses examples like cricket, movies, food
- Says things like "Arre yaar...", "Pakka yaad rakhna!", "Exam mein aayega!"

**SUBJECT:** {subject}
**CHAPTER:** {chapter}

**SOURCE CONTENT:**
{text}

**SCRIPT REQUIREMENTS:**
1. Start with a catchy intro (Didi welcomes, Bhaiya hypes up the topic)
2. Break down concepts in simple Hinglish
3. Include exam tips and common mistakes
4. Add memory tricks (mnemonics) where possible
5. End with quick revision points
6. Keep it conversational, fun, NOT boring lecture

**FORMAT YOUR OUTPUT EXACTLY LIKE THIS:**
DIDI: [dialogue]
BHAIYA: [dialogue]
DIDI: [dialogue]
...

**IMPORTANT:**
- Use Hinglish naturally (not forced)
- Keep sentences short (for TTS clarity)
- Include pauses with "..." 
- Make it sound like two friends teaching, not robots
- Target 8-12 minutes of speaking time

Generate the complete script now:"""

    def _clean_script(self, script: str) -> str:
        """Clean and format the generated script"""
        # Remove any markdown formatting
        script = script.replace("**", "")
        script = script.replace("```", "")
        
        # Ensure proper speaker labels
        lines = script.split("\n")
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Normalize speaker labels
            if line.upper().startswith("DIDI:"):
                line = "DIDI:" + line[5:]
            elif line.upper().startswith("BHAIYA:"):
                line = "BHAIYA:" + line[7:]
            
            cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    def _get_demo_script(self, subject: str, chapter: str) -> str:
        """Return a demo script for testing"""
        return f"""DIDI: Hello students! Swagat hai aapka Commute and Learn mein! Aaj hum padhenge {subject} ka ek bahut important chapter... {chapter}!

BHAIYA: Arre waaah! Yeh toh mera favorite topic hai! Dekho guys, yeh chapter JEE aur NEET dono mein aata hai... almost har saal!

DIDI: Bilkul sahi Bhaiya! Toh chalo, ek ek concept ko simple tarike se samajhte hain... Pehle basics clear karte hain.

BHAIYA: Haan haan! Dekho yaar, isko samajhne ke liye ek example lete hain... Cricket ki tarah socho!

DIDI: Achha idea hai! Toh socho... jab Virat Kohli batting karta hai, toh wo ball ko force lagata hai, right? Isse hi hum physics mein force kehte hain.

BHAIYA: Exactly! Aur jo formula yaad rakhna hai wo hai F equals m into a... Force equals mass into acceleration... Pakka yaad rakhna!

DIDI: Ab dekho beta, yeh formula kitna powerful hai... Agar mass badh jaaye, same force pe acceleration kam ho jayega...

BHAIYA: Arre haan! Isliye heavy truck slow start hota hai aur bike jaldi pick up karti hai... Same engine power, different mass!

DIDI: Waah Bhaiya! Kya example diya! Ab students ko samajh aa gaya hoga...

BHAIYA: Aur ek important tip for exam... Jab bhi force wala question aaye, pehle Free Body Diagram banao... Time bachega aur galti nahi hogi!

DIDI: Haan yeh bahut zaroori hai! FBD se sab forces clearly dikh jaate hain... confuse nahi hoge!

BHAIYA: Chalo ab kuch quick revision points... Number one: Newton ka first law... objects apni state change nahi karte jab tak force na lage!

DIDI: Number two: F equals ma... force mass aur acceleration se related hai!

BHAIYA: Number three: Action reaction... har force ka equal aur opposite reaction hota hai!

DIDI: Perfect! Toh students, aaj ka podcast yahin khatam hota hai... Hope you enjoyed learning with us!

BHAIYA: Haan guys! Kal phir milte hain next topic ke saath... Tab tak practice karo aur notes revise karo!

DIDI: Bye bye! Happy studying!

BHAIYA: All the best! Crack karo JEE aur NEET! Ciao!"""
