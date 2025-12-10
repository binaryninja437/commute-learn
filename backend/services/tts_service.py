"""
TTS Service - Multi-voice using Edge TTS
Didi = Female Hindi voice
Bhaiya = Male Hindi voice
"""

import os
import re
import asyncio
import tempfile
import edge_tts
from pydub import AudioSegment

from dotenv import load_dotenv
load_dotenv()


class TTSService:
    # Real Hindi voices - Male and Female
    VOICES = {
        "DIDI": "hi-IN-SwaraNeural",      # Female Hindi
        "BHAIYA": "hi-IN-MadhurNeural",    # Male Hindi
    }

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        print("[TTS] Service initialized with Edge TTS (Multi-voice)")
        print(f"[TTS] Didi voice: {self.VOICES['DIDI']}")
        print(f"[TTS] Bhaiya voice: {self.VOICES['BHAIYA']}")

    async def generate_audio(self, script: str, output_path: str) -> int:
        """Convert script to MP3 with different voices for Didi and Bhaiya"""
        print(f"[TTS] Generating multi-voice audio...")
        print(f"[TTS] Script length: {len(script)} characters")

        try:
            # Parse script into segments
            segments = self._parse_script(script)
            print(f"[TTS] Found {len(segments)} dialogue segments")

            if not segments:
                segments = [("DIDI", script)]

            audio_files = []

            for i, (speaker, text) in enumerate(segments):
                if not text.strip() or len(text.strip()) < 2:
                    continue

                segment_path = os.path.join(self.temp_dir, f"seg_{i}.mp3")
                voice = self.VOICES.get(speaker, self.VOICES["DIDI"])

                clean_text = self._clean_text(text)

                print(f"[TTS] Segment {i}: {speaker} ({voice}) - {len(clean_text)} chars")

                try:
                    # Generate audio with Edge TTS
                    communicate = edge_tts.Communicate(clean_text, voice)
                    await communicate.save(segment_path)
                    audio_files.append(segment_path)

                except Exception as e:
                    print(f"[TTS] Edge TTS failed for segment {i}: {e}")
                    # Fallback to gTTS
                    try:
                        from gtts import gTTS
                        tts = gTTS(text=clean_text, lang='hi')
                        tts.save(segment_path)
                        audio_files.append(segment_path)
                        print(f"[TTS] Used gTTS fallback for segment {i}")
                    except Exception as e2:
                        print(f"[TTS] gTTS fallback also failed: {e2}")
                        continue

            if not audio_files:
                print("[TTS] No audio generated!")
                # Create error message audio
                from gtts import gTTS
                tts = gTTS("Audio generation failed. Please try again.", lang='en')
                tts.save(output_path)
                return 5

            # Combine all segments
            print(f"[TTS] Combining {len(audio_files)} audio segments...")
            duration = self._combine_audio(audio_files, output_path)

            # Cleanup
            for f in audio_files:
                try:
                    os.remove(f)
                except:
                    pass

            print(f"[TTS] SUCCESS! Duration: {duration} seconds")
            return duration

        except Exception as e:
            print(f"[TTS] ERROR: {e}")
            import traceback
            traceback.print_exc()

            # Emergency fallback
            try:
                from gtts import gTTS
                clean_script = re.sub(r'(DIDI:|BHAIYA:)', '', script)
                tts = gTTS(text=clean_script[:3000], lang='hi')
                tts.save(output_path)
                return 60
            except:
                raise

    def _parse_script(self, script: str):
        """Parse script into (speaker, text) tuples"""
        segments = []
        current_speaker = "DIDI"
        current_text = []

        lines = script.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for speaker change
            if line.upper().startswith('DIDI:'):
                # Save previous segment
                if current_text:
                    segments.append((current_speaker, ' '.join(current_text)))
                    current_text = []
                current_speaker = "DIDI"
                text = line[5:].strip()
                if text:
                    current_text.append(text)

            elif line.upper().startswith('BHAIYA:'):
                # Save previous segment
                if current_text:
                    segments.append((current_speaker, ' '.join(current_text)))
                    current_text = []
                current_speaker = "BHAIYA"
                text = line[7:].strip()
                if text:
                    current_text.append(text)
            else:
                # Continue current speaker
                current_text.append(line)

        # Don't forget last segment
        if current_text:
            segments.append((current_speaker, ' '.join(current_text)))

        return segments

    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        # Remove markdown/special chars
        text = re.sub(r'[*_#`\[\]]', '', text)
        text = text.replace('...', ', ')
        text = text.replace('  ', ' ')

        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)

        return text.strip()

    def _combine_audio(self, audio_files: list, output_path: str) -> int:
        """Combine audio segments with small pauses"""
        combined = AudioSegment.empty()
        pause = AudioSegment.silent(duration=400)  # 400ms pause between speakers

        for i, audio_file in enumerate(audio_files):
            try:
                segment = AudioSegment.from_mp3(audio_file)
                combined += segment

                # Add pause between segments (not after last)
                if i < len(audio_files) - 1:
                    combined += pause

            except Exception as e:
                print(f"[TTS] Error loading {audio_file}: {e}")
                continue

        if len(combined) == 0:
            combined = AudioSegment.silent(duration=1000)

        # Add fade in/out for polish
        if len(combined) > 1000:
            combined = combined.fade_in(300).fade_out(300)

        # Export
        combined.export(output_path, format="mp3", bitrate="128k")

        return int(len(combined) / 1000)
