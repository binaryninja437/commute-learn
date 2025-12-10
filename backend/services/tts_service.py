"""
TTS Service - Multi-voice using different gTTS settings
Didi = Female voice (Hindi)
Bhaiya = Male voice (English-India with different accent)
"""

import os
import re
import asyncio
import tempfile
from pydub import AudioSegment
from pydub.effects import speedup
from gtts import gTTS

from dotenv import load_dotenv
load_dotenv()


class TTSService:
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        print("[TTS] Service initialized with Multi-voice gTTS")
        print("[TTS] Didi: Hindi female (hi)")
        print("[TTS] Bhaiya: English-India male (en, tld=co.in, slower)")

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
                clean_text = self._clean_text(text)

                print(f"[TTS] Segment {i}: {speaker} - {len(clean_text)} chars")

                try:
                    if speaker == "DIDI":
                        # Female voice: Hindi, normal speed
                        tts = gTTS(text=clean_text, lang='hi', slow=False)
                        tts.save(segment_path)
                    else:  # BHAIYA
                        # Male voice: English-India, slower and deeper
                        tts = gTTS(text=clean_text, lang='en', tld='co.in', slow=False)
                        tts.save(segment_path)

                        # Make it sound different (lower pitch via speed manipulation)
                        audio = AudioSegment.from_mp3(segment_path)
                        # Slow down slightly and lower pitch
                        audio = audio._spawn(audio.raw_data, overrides={
                            "frame_rate": int(audio.frame_rate * 0.90)
                        }).set_frame_rate(audio.frame_rate)
                        audio.export(segment_path, format="mp3")

                    audio_files.append(segment_path)

                except Exception as e:
                    print(f"[TTS] Segment {i} failed: {e}")
                    # Try fallback
                    try:
                        tts = gTTS(text=clean_text, lang='hi')
                        tts.save(segment_path)
                        audio_files.append(segment_path)
                    except Exception as e2:
                        print(f"[TTS] Fallback also failed: {e2}")
                        continue

            if not audio_files:
                print("[TTS] No audio generated!")
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
        pause = AudioSegment.silent(duration=500)  # 500ms pause between speakers

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
