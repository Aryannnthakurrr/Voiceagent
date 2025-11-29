"""
Real-time Voice Agent using OpenAI's Realtime API
Handles live audio conversation for hospital inquiries
"""

import asyncio
import base64
import os
import sys
import threading
import queue
from typing import Any

import numpy as np
import sounddevice as sd

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import (
    OPENAI_API_KEY,
    REALTIME_MODEL,
    SAMPLE_RATE,
    CHANNELS,
    SYSTEM_INSTRUCTIONS,
    HOSPITAL_NAME
)

try:
    from openai import AsyncOpenAI
    from openai.resources.beta.realtime.realtime import AsyncRealtimeConnection
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)


class AudioPlayer:
    """
    Threaded audio player with instant interrupt capability.
    Uses a queue that can be cleared immediately when user speaks.
    """
    
    def __init__(self, sample_rate=24000):
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.stop_flag = threading.Event()
        self.interrupt_flag = threading.Event()
        self.thread = None
        self.stream = None
        
    def _player_thread(self):
        """Background thread that plays audio from queue"""
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            blocksize=256,  # Very small for quick response
        )
        self.stream.start()
        
        while not self.stop_flag.is_set():
            try:
                # Get audio with timeout so we can check flags
                audio_data = self.audio_queue.get(timeout=0.05)
                
                # Check if interrupted before playing
                if self.interrupt_flag.is_set():
                    continue  # Discard this audio
                    
                # Play in small chunks so we can interrupt mid-playback
                chunk_size = 1200  # ~50ms at 24kHz
                for i in range(0, len(audio_data), chunk_size):
                    if self.interrupt_flag.is_set():
                        break  # Stop mid-chunk if interrupted
                    chunk = audio_data[i:i+chunk_size]
                    self.stream.write(chunk)
                    
            except queue.Empty:
                continue
            except Exception as e:
                pass
                
        if self.stream:
            self.stream.stop()
            self.stream.close()
        
    def start(self):
        """Start the audio player thread"""
        self.stop_flag.clear()
        self.interrupt_flag.clear()
        self.thread = threading.Thread(target=self._player_thread, daemon=True)
        self.thread.start()
        print("🔊 Audio output initialized")
        
    def play(self, audio_bytes: bytes, response_id: str = None):
        """Queue audio for playback"""
        if self.interrupt_flag.is_set():
            return  # Don't queue if interrupted
        try:
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            self.audio_queue.put(audio_array)
        except:
            pass
    
    def cancel_current(self):
        """INSTANTLY stop all audio and clear queue"""
        # Set interrupt flag - player thread will stop immediately
        self.interrupt_flag.set()
        
        # Clear the queue
        while True:
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        # Small delay then allow new audio
        threading.Timer(0.1, self._reset_interrupt).start()
    
    def _reset_interrupt(self):
        """Reset interrupt flag to allow new audio"""
        self.interrupt_flag.clear()
    
    def set_response(self, response_id: str):
        """Called when new response starts - clear interrupt"""
        self.interrupt_flag.clear()
    
    def reset(self):
        """Alias for cancel_current"""
        self.cancel_current()
    
    def stop(self):
        """Stop the player thread"""
        self.stop_flag.set()
        if self.thread:
            self.thread.join(timeout=1)


class RealtimeVoiceAgent:
    """
    A real-time voice agent that uses OpenAI's Realtime API
    for live speech-to-speech conversation.
    """
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.audio_player = AudioPlayer(SAMPLE_RATE)
        self.connection: AsyncRealtimeConnection | None = None
        self.should_send_audio = asyncio.Event()
        self.connected = asyncio.Event()
        self.last_audio_item_id = None
        
    async def send_mic_audio(self):
        """Continuously capture and send audio from microphone"""
        read_size = int(SAMPLE_RATE * 0.02)  # 20ms chunks
        
        stream = sd.InputStream(
            channels=CHANNELS,
            samplerate=SAMPLE_RATE,
            dtype=np.int16,
        )
        stream.start()
        
        sent_audio = False
        audio_level_counter = 0
        
        try:
            while True:
                # Wait for enough audio data
                if stream.read_available < read_size:
                    await asyncio.sleep(0.005)
                    continue
                
                data, _ = stream.read(read_size)
                
                # Calculate audio level for debugging (every ~1 second)
                audio_level_counter += 1
                if audio_level_counter >= 50:  # Every 50 * 20ms = 1 second
                    level = np.abs(data).mean()
                    if level > 100:  # Only show if there's actual sound
                        print(f"🔊 Audio level: {int(level)}", end="\r")
                    audio_level_counter = 0
                
                # Wait for connection
                await self.connected.wait()
                
                if self.connection:
                    # Send audio to the API
                    audio_b64 = base64.b64encode(data.tobytes()).decode('utf-8')
                    await self.connection.input_audio_buffer.append(audio=audio_b64)
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"\nAudio capture error: {e}")
        finally:
            stream.stop()
            stream.close()
    
    async def handle_realtime_connection(self):
        """Main connection handler"""
        try:
            async with self.client.beta.realtime.connect(model=REALTIME_MODEL) as conn:
                self.connection = conn
                self.connected.set()
                
                # Configure session with voice and interrupt support
                # Best voices for natural sound: coral, verse, marin, cedar
                await conn.session.update(session={
                    "modalities": ["text", "audio"],
                    "voice": "coral",  # Warm, friendly, natural female voice
                    "instructions": SYSTEM_INSTRUCTIONS,
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.3,  # Lower = more sensitive to user speech
                        "prefix_padding_ms": 200,
                        "silence_duration_ms": 400,
                        "create_response": True,
                        "interrupt_response": True  # Enable barge-in / interruption
                    }
                })
                
                print("✅ Connected to OpenAI Realtime API")
                print("🗣️  Voice: Coral (Natural Female) | Language: Hinglish")
                
                acc_items: dict[str, Any] = {}
                
                async for event in conn:
                    # Handle user interruption - stop current response IMMEDIATELY
                    if event.type == "input_audio_buffer.speech_started":
                        # User started speaking - cancel current response
                        # This marks the response as cancelled so remaining audio won't play
                        self.audio_player.cancel_current()
                        try:
                            await conn.response.cancel()
                        except:
                            pass  # No active response to cancel
                        print("\n🔇 [Interrupted] 🎤 Listening...", end="\r")
                        continue
                    
                    # Response was cancelled (interrupted) - ensure audio stops
                    if event.type == "response.cancelled":
                        self.audio_player.cancel_current()
                        continue
                    
                    # Session events
                    if event.type == "session.created":
                        print("📡 Session established")
                        continue
                    
                    if event.type == "session.updated":
                        print("⚙️  Session configured")
                        print("\n" + "="*50)
                        print("🎤 READY! Start speaking into your microphone...")
                        print("="*50 + "\n")
                        print("="*50 + "\n")
                        continue
                    
                    # Audio output from AI - queue for playback
                    if event.type in ("response.audio.delta", "response.output_audio.delta"):
                        audio_bytes = base64.b64decode(event.delta)
                        self.audio_player.play(audio_bytes)
                        continue
                    
                    # AI transcript (what the AI is saying)
                    # Handle both old and new event names
                    if event.type in ("response.audio_transcript.delta", "response.output_audio_transcript.delta"):
                        # Only accumulate, don't print every delta
                        try:
                            item_id = getattr(event, 'item_id', 'default')
                            text = acc_items.get(item_id, "")
                            acc_items[item_id] = text + event.delta
                        except:
                            pass
                        continue
                    
                    if event.type in ("response.audio_transcript.done", "response.output_audio_transcript.done"):
                        # Print the complete transcript once at the end
                        try:
                            item_id = getattr(event, 'item_id', 'default')
                            if item_id in acc_items:
                                print(f"🤖 AI: {acc_items[item_id]}")
                        except:
                            pass
                        continue
                    
                    # User's transcribed speech
                    if event.type == "conversation.item.input_audio_transcription.completed":
                        if hasattr(event, 'transcript') and event.transcript:
                            print(f"\n👤 You said: \"{event.transcript}\"")
                        continue
                    
                    # Input audio buffer events
                    if event.type == "input_audio_buffer.speech_stopped":
                        print("⏳ [Processing...]", end="\r")
                        continue
                    
                    # Error handling
                    if event.type == "error":
                        error_msg = str(getattr(event, 'error', event))
                        # Suppress cancel errors (normal during interruptions)
                        if 'response_cancel_not_active' not in error_msg:
                            print(f"\n❌ API Error: {error_msg}")
                        continue
                        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"\n❌ Connection error: {e}")
            import traceback
            traceback.print_exc()
    
    async def run_async(self):
        """Main async entry point"""
        print(f"\n{'='*60}")
        print(f"🏥 Welcome to {HOSPITAL_NAME} Voice Assistant")
        print(f"{'='*60}")
        print("\n🎤 Speak into your microphone to ask questions about:")
        print("   • Doctors and their availability")
        print("   • Department information") 
        print("   • Hospital facilities and timings")
        print("   • Which specialist to consult for your symptoms")
        print("\n⏹️  Press Ctrl+C to stop the conversation")
        print(f"{'='*60}\n")
        
        self.audio_player.start()
        
        try:
            # Create tasks for both audio capture and connection handling
            audio_task = asyncio.create_task(self.send_mic_audio())
            connection_task = asyncio.create_task(self.handle_realtime_connection())
            
            # Wait for both tasks (they run forever until cancelled)
            await asyncio.gather(audio_task, connection_task)
                
        except asyncio.CancelledError:
            pass
        finally:
            self.audio_player.stop()
            print("\n🔴 Voice agent stopped.")
    
    def run(self):
        """Synchronous entry point - runs the async event loop"""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thank you for using our voice assistant.")


class VoiceAgent:
    """
    Legacy VoiceAgent class for backward compatibility.
    Wraps the RealtimeVoiceAgent.
    """
    
    def __init__(self, speech_recognition=None, text_to_speech=None, query_handler=None):
        self.realtime_agent = RealtimeVoiceAgent()
        self.speech_recognition = speech_recognition
        self.text_to_speech = text_to_speech
        self.query_handler = query_handler

    def listen(self):
        """Legacy method - not used in realtime mode"""
        pass

    def respond(self, query):
        """Legacy method - not used in realtime mode"""
        pass
    
    def listen_and_respond(self):
        """Main method to start the voice agent"""
        self.realtime_agent.run()


# Allow running directly
if __name__ == "__main__":
    agent = RealtimeVoiceAgent()
    agent.run()# Allow running directly
if __name__ == "__main__":
    agent = RealtimeVoiceAgent()
    agent.run()