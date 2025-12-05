"""
TTS Service using gTTS (Google Text-to-Speech)
Free, reliable, works immediately
"""

import os
from dotenv import load_dotenv
load_dotenv()

import re
import asyncio
from gtts import gTTS
from pydub import AudioSegment
import tempfile


class TTSService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        print("[TTS] Service initialized with gTTS")

    async def generate_audio(self, script: str, output_path: str) -> int:
        """Convert script to MP3 audio"""
        print(f"[TTS] Generating audio for {len(script)} characters")
        print(f"[TTS] Output: {output_path}")

        try:
            # Parse script into segments
            segments = self._parse_script(script)
            print(f"[TTS] Parsed {len(segments)} segments")

            if not segments:
                print("[TTS] No segments found, using full script")
                segments = [("DIDI", script)]

            audio_files = []

            for i, (speaker, text) in enumerate(segments):
                if not text.strip():
                    continue

                segment_path = os.path.join(self.temp_dir, f"seg_{i}.mp3")

                # Use different languages for variety
                # hi = Hindi, en-IN = Indian English
                lang = "hi" if speaker == "DIDI" else "en"
                tld = "co.in"  # Indian accent for English

                try:
                    # Clean text for TTS
                    clean_text = self._clean_text(text)

                    if len(clean_text) < 2:
                        continue

                    print(f"[TTS] Segment {i}: {speaker} - {len(clean_text)} chars")

                    # Generate audio
                    tts = gTTS(text=clean_text, lang=lang, tld=tld)
                    tts.save(segment_path)
                    audio_files.append(segment_path)

                except Exception as e:
                    print(f"[TTS] Segment {i} failed: {e}")
                    # Try with English as fallback
                    try:
                        tts = gTTS(text=clean_text, lang="en")
                        tts.save(segment_path)
                        audio_files.append(segment_path)
                    except:
                        continue

            if not audio_files:
                print("[TTS] No audio generated, creating placeholder")
                tts = gTTS(text="Audio generation failed. Please try again.", lang="en")
                tts.save(output_path)
                return 5

            # Combine all segments
            print(f"[TTS] Combining {len(audio_files)} audio files")
            duration = self._combine_audio(audio_files, output_path)

            # Cleanup temp files
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

            # Create a fallback audio
            try:
                tts = gTTS(text="Sorry, audio generation encountered an error.", lang="en")
                tts.save(output_path)
                return 5
            except:
                raise

    def _parse_script(self, script: str):
        """Parse script into (speaker, text) tuples"""
        segments = []
        current_speaker = "DIDI"

        lines = script.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.upper().startswith("DIDI:"):
                current_speaker = "DIDI"
                text = line[5:].strip()
            elif line.upper().startswith("BHAIYA:"):
                current_speaker = "BHAIYA"
                text = line[7:].strip()
            else:
                text = line

            if text:
                segments.append((current_speaker, text))

        return segments

    def _clean_text(self, text: str) -> str:
        """Clean text for TTS"""
        # Remove special characters
        text = re.sub(r'[*_#`]', '', text)
        text = re.sub(r'\[.*?\]', '', text)  # Remove [brackets]
        text = text.replace("...", ", ")
        text = text.replace("  ", " ")
        return text.strip()

    def _combine_audio(self, audio_files: list, output_path: str) -> int:
        """Combine audio files into one"""
        combined = AudioSegment.empty()
        pause = AudioSegment.silent(duration=300)  # 300ms pause

        for audio_file in audio_files:
            try:
                segment = AudioSegment.from_mp3(audio_file)
                combined += segment + pause
            except Exception as e:
                print(f"[TTS] Error loading {audio_file}: {e}")
                continue

        if len(combined) == 0:
            # Create minimal audio
            combined = AudioSegment.silent(duration=1000)

        # Export
        combined.export(output_path, format="mp3", bitrate="128k")

        return int(len(combined) / 1000)  # Duration in seconds
