"""
Audio generation module for converting scripts to speech with word timings
"""

import boto3
import json
import html
import os
from datetime import datetime
from typing import Dict, List, Tuple

# Initialize AWS clients
polly = boto3.client('polly', region_name='us-west-2')
s3 = boto3.client('s3')

class AudioGenerator:
    def __init__(self, bucket: str, voice_id: str = 'Joanna'):
        """Initialize audio generator with S3 bucket and voice settings"""
        self.bucket = bucket
        self.voice_id = voice_id if voice_id in [
            "Joanna", "Matthew", "Amy", "Emma", "Brian", "Justin", 
            "Kendra", "Kimberly", "Salli", "Joey", "Ivy", "Ruth"
        ] else "Joanna"
    
    def generate_audio(self, script: str, run_id: str) -> Dict:
        """Generate audio from script with word timings"""
        try:
            print(f"🎙️ Generating audio for run {run_id} with voice {self.voice_id}...")
            
            # Convert script to SSML
            ssml = self._to_ssml(script)
            print(f"📝 SSML length: {len(ssml)} characters")
            
            # Get word timings first
            word_timings = self._get_word_timings(ssml)
            print(f"⏱️ Generated {len(word_timings)} word timings")
            
            # Generate audio
            audio_bytes = self._synthesize_audio(ssml)
            print(f"🔊 Generated {len(audio_bytes)} bytes of audio")
            
            # Save to S3
            day = datetime.utcnow().strftime("%Y-%m-%d")
            audio_key = f"audio/{day}/voice-{run_id}.mp3"
            
            s3.put_object(
                Bucket=self.bucket,
                Key=audio_key,
                Body=audio_bytes,
                ContentType="audio/mpeg",
                CacheControl="public, max-age=3600",
                Metadata={
                    'generated-by': 'curio-news-ai',
                    'voice-id': self.voice_id,
                    'run-id': run_id
                }
            )
            
            # Generate public URL
            audio_url = f"https://{self.bucket}.s3.us-west-2.amazonaws.com/{audio_key}"
            print(f"🌐 Audio URL: {audio_url}")
            
            return {
                'success': True,
                'audio_url': audio_url,
                'word_timings': word_timings,
                'duration': word_timings[-1]['end'] if word_timings else 0
            }
            
        except Exception as e:
            print(f"❌ Audio generation error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e)
            }
    
    def _to_ssml(self, text: str) -> str:
        """Convert text to SSML with natural pauses"""
        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Escape special characters
        safe = html.escape(text, quote=False)
        
        # Add natural conversational pauses
        safe = safe.replace("...", "<break time='500ms'/>")  # Dramatic pauses
        safe = safe.replace(", ", ", <break time='200ms'/>")  # Comma pauses
        safe = safe.replace(". ", ". <break time='400ms'/>")  # Sentence breaks
        safe = safe.replace("? ", "? <break time='350ms'/>")  # Question pauses
        safe = safe.replace("! ", "! <break time='300ms'/>")  # Exclamation pauses
        
        # Paragraph breaks for topic transitions
        safe = safe.replace("\n\n", "<break time='600ms'/>")
        safe = safe.replace("\n", "<break time='250ms'/>")
        
        # Slightly slower pace for better clarity
        return f"<speak><prosody rate='95%'>{safe}</prosody></speak>"
    
    def _get_word_timings(self, ssml: str) -> List[Dict]:
        """Get word timing data from Polly"""
        try:
            # Request word timing marks
            response = polly.synthesize_speech(
                Text=ssml,
                TextType="ssml",
                VoiceId=self.voice_id,
                Engine="neural",
                OutputFormat="json",
                SpeechMarkTypes=["word"]
            )
            
            # Parse timing data
            word_timings = []
            marks_data = response["AudioStream"].read().decode('utf-8')
            
            for line in marks_data.strip().split('\n'):
                if line.strip():
                    mark = json.loads(line)
                    if mark.get('type') == 'word':
                        word_timings.append({
                            'word': mark.get('value', ''),
                            'start': mark.get('time', 0) / 1000.0,  # Convert ms to seconds
                            'end': (mark.get('time', 0) + 500) / 1000.0  # Estimate end time
                        })
            
            return word_timings
            
        except Exception as e:
            print(f"❌ Word timing error: {e}")
            # Fallback to estimated timings
            return self._estimate_word_timings(ssml)
    
    def _synthesize_audio(self, ssml: str) -> bytes:
        """Generate audio using Polly"""
        try:
            # Generate audio with neural engine
            response = polly.synthesize_speech(
                Text=ssml,
                TextType="ssml",
                VoiceId=self.voice_id,
                Engine="neural",
                OutputFormat="mp3"
            )
            
            return response["AudioStream"].read()
            
        except Exception as e:
            print(f"❌ Audio synthesis error: {e}")
            # Try with basic SSML
            basic_ssml = f"<speak>{html.escape(ssml, quote=False)}</speak>"
            response = polly.synthesize_speech(
                Text=basic_ssml,
                TextType="ssml",
                VoiceId=self.voice_id,
                Engine="neural",
                OutputFormat="mp3"
            )
            
            return response["AudioStream"].read()
    
    def _estimate_word_timings(self, text: str) -> List[Dict]:
        """Fallback: estimate word timings based on average speech rate"""
        import re
        
        # Clean text and split into words
        clean_text = re.sub(r'[^\w\s]', ' ', text)
        words = [w for w in clean_text.split() if w.strip()]
        
        # Average speech rate: ~150 words per minute = 2.5 words per second
        words_per_second = 2.2  # Slightly slower for news reading
        
        word_timings = []
        current_time = 0.0
        
        for word in words:
            # Estimate duration based on word length
            base_duration = 1.0 / words_per_second
            length_factor = max(0.7, min(1.5, len(word) / 6.0))
            duration = base_duration * length_factor
            
            word_timings.append({
                'word': word,
                'start': round(current_time, 2),
                'end': round(current_time + duration, 2)
            })
            
            current_time += duration
            
            # Add pauses for punctuation
            if any(punct in text[text.find(word):text.find(word) + len(word) + 5] 
                   for punct in ['.', '!', '?']):
                current_time += 0.3  # Sentence pause
            elif ',' in text[text.find(word):text.find(word) + len(word) + 3]:
                current_time += 0.15  # Comma pause
        
        return word_timings