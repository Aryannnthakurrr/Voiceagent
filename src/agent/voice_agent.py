"""
Real-time Voice Agent using OpenAI's Realtime API
Handles live audio conversation for hospital inquiries
Now with TOOLS for cost-efficient data retrieval!
Includes COST TRACKING for all API usage.
"""

import asyncio
import base64
import json
import os
import sys
import threading
import queue
import time
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

# Import tools for function calling
from agent.tools import TOOLS, handle_tool_call

# Import cost tracker
from utils.cost_tracker import init_tracker, get_tracker

try:
    from openai import AsyncOpenAI
    from openai.resources.beta.realtime.realtime import AsyncRealtimeConnection
except ImportError:
    print("Please install openai: pip install openai")
    sys.exit(1)


import platform


class AudioPlayer:
    """
    Threaded audio player with instant interrupt capability.
    Uses a queue that can be cleared immediately when user speaks.
    Cross-platform compatible (Windows, Mac, Linux).
    """
    
    def __init__(self, sample_rate=24000, verbose=False):
        self.sample_rate = sample_rate
        self.verbose = verbose
        self.audio_queue = queue.Queue()
        self.stop_flag = threading.Event()
        self.interrupt_flag = threading.Event()
        self.thread = None
        self.stream = None
        self.is_mac = platform.system() == "Darwin"
        
    def _player_thread(self):
        """Background thread that plays audio from queue"""
        # Mac needs larger buffer to avoid stuttering
        blocksize = 4800 if self.is_mac else 256
        
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.int16,
            blocksize=blocksize,
            latency='low' if not self.is_mac else 'high',
        )
        self.stream.start()
        
        # Buffer to accumulate audio for smoother playback on Mac
        audio_buffer = []
        min_buffer_size = 4800 if self.is_mac else 0  # ~200ms buffer on Mac
        
        while not self.stop_flag.is_set():
            try:
                # Get audio with timeout so we can check flags
                audio_data = self.audio_queue.get(timeout=0.1)
                
                # Check if interrupted before playing
                if self.interrupt_flag.is_set():
                    audio_buffer = []  # Clear buffer on interrupt
                    continue
                
                if self.is_mac:
                    # Accumulate audio in buffer for smoother playback
                    audio_buffer.append(audio_data)
                    total_samples = sum(len(a) for a in audio_buffer)
                    
                    # Play when buffer is large enough
                    if total_samples >= min_buffer_size:
                        combined = np.concatenate(audio_buffer)
                        audio_buffer = []
                        
                        if not self.interrupt_flag.is_set():
                            self.stream.write(combined)
                else:
                    # Windows/Linux: play in small chunks for quick interrupt
                    chunk_size = 1200  # ~50ms at 24kHz
                    for i in range(0, len(audio_data), chunk_size):
                        if self.interrupt_flag.is_set():
                            break
                        chunk = audio_data[i:i+chunk_size]
                        self.stream.write(chunk)
                    
            except queue.Empty:
                # On Mac, flush any remaining buffer during silence
                if self.is_mac and audio_buffer and not self.interrupt_flag.is_set():
                    combined = np.concatenate(audio_buffer)
                    audio_buffer = []
                    self.stream.write(combined)
                continue
            except Exception as e:
                if self.verbose:
                    print(f"[AUDIO] Playback error: {e}")
                
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except:
                pass
        
    def start(self):
        """Start the audio player thread"""
        self.stop_flag.clear()
        self.interrupt_flag.clear()
        self.thread = threading.Thread(target=self._player_thread, daemon=True)
        self.thread.start()
        if self.verbose:
            platform_name = "Mac" if self.is_mac else platform.system()
            print(f"[AUDIO] Output initialized ({platform_name})")
        
    def play(self, audio_bytes: bytes, response_id: str = None):
        """Queue audio for playback"""
        if self.interrupt_flag.is_set():
            return  # Don't queue if interrupted
        try:
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
            if len(audio_array) > 0:  # Only queue non-empty audio
                self.audio_queue.put(audio_array)
        except Exception as e:
            if self.verbose:
                print(f"[AUDIO] Queue error: {e}")
    
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
    
    Includes conversation history management to control costs.
    Includes COST TRACKING for all API usage.
    """
    
    # Configuration for conversation history
    MAX_TURNS_BEFORE_SUMMARY = 4  # Summarize after this many exchanges
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.audio_player = AudioPlayer(SAMPLE_RATE, verbose=verbose)
        self.connection: AsyncRealtimeConnection | None = None
        self.should_send_audio = asyncio.Event()
        self.connected = asyncio.Event()
        self.last_audio_item_id = None
        
        # Conversation tracking for summarization
        self.turn_count = 0
        self.conversation_summary = ""  # Compressed history
        self.recent_exchanges = []  # Last few exchanges (text only)
        
        # Cost tracking
        self.cost_tracker = init_tracker(verbose=verbose)
        self.turn_start_time = None  # Track audio duration
        self.audio_output_chars = 0  # Estimate output duration from text length
        
        # Echo/interrupt protection - prevent AI audio from triggering VAD
        self.ai_speaking = False
        self.ai_speech_end_time = 0
        self.ECHO_COOLDOWN = 0.8  # Seconds to wait after AI stops before accepting interrupts
    
    async def summarize_conversation(self):
        """
        Use GPT-4o-mini to summarize conversation history cheaply.
        This compresses old context to save tokens.
        """
        if not self.recent_exchanges:
            return
        
        # Build text of recent exchanges
        exchanges_text = "\n".join([
            f"User: {ex.get('user', 'unknown')}\nAssistant: {ex.get('assistant', 'unknown')}"
            for ex in self.recent_exchanges
        ])
        
        try:
            # Use GPT-4o-mini for cheap summarization
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize this hospital reception conversation in 2-3 sentences. Focus on: patient's issue, any doctor/department mentioned, and what was resolved or pending. Be concise."
                    },
                    {
                        "role": "user", 
                        "content": f"Previous summary: {self.conversation_summary or 'None'}\n\nNew exchanges:\n{exchanges_text}"
                    }
                ],
                max_tokens=150
            )
            
            # Log cost for summarization
            usage = response.usage
            if usage:
                self.cost_tracker.log_chat_completion(
                    model="gpt-4o-mini",
                    input_tokens=usage.prompt_tokens,
                    output_tokens=usage.completion_tokens,
                    purpose="conversation_summary"
                )
            
            self.conversation_summary = response.choices[0].message.content
            self.recent_exchanges = []  # Clear after summarizing
            if self.verbose:
                print(f"[INFO] History compressed")
            
        except Exception as e:
            if self.verbose:
                print(f"[WARN] Summary failed: {e}")
    
    async def inject_summary_context(self):
        """Inject the conversation summary into the session if we have one."""
        if self.conversation_summary and self.connection:
            try:
                # Add summary as a system message in conversation
                await self.connection.conversation.item.create(
                    item={
                        "type": "message",
                        "role": "system",
                        "content": [
                            {
                                "type": "input_text",
                                "text": f"[Previous conversation summary: {self.conversation_summary}]"
                            }
                        ]
                    }
                )
            except Exception as e:
                pass  # Non-critical
    
    async def truncate_old_items(self):
        """Remove old conversation items to prevent context from growing too large."""
        # The Realtime API doesn't have a direct "list items" method,
        # so we track turn count and reset session periodically
        if self.turn_count >= self.MAX_TURNS_BEFORE_SUMMARY * 2:
            if self.verbose:
                print("[INFO] Resetting session to manage costs...")
            # Summarize before reset
            await self.summarize_conversation()
            self.turn_count = 0
        
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
                    if self.verbose and level > 100:  # Only show if verbose and actual sound
                        print(f"[MIC] Level: {int(level)}", end="\r")
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
                
                # Configure session with voice, tools, and interrupt support
                # Best voices for natural sound: coral, verse, marin, cedar
                await conn.session.update(session={
                    "modalities": ["text", "audio"],
                    "voice": "coral",  # Warm, friendly, natural female voice
                    "instructions": SYSTEM_INSTRUCTIONS,
                    "tools": TOOLS,  # Register tools for function calling
                    "tool_choice": "auto",  # Let model decide when to use tools
                    # Removed input_audio_transcription to save Whisper tokens!
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.6,  # Higher = less sensitive (prevents echo/noise triggers)
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 700,  # Longer pause needed to end speech
                        "create_response": True,
                        "interrupt_response": True  # Enable barge-in / interruption
                    }
                })
                
                print("[OK] Connected to OpenAI Realtime API")
                if self.verbose:
                    print("[INFO] Voice: Coral (Natural Female) | Language: Hinglish")
                    print("[INFO] Tools: 7 functions for hospital data retrieval")
                
                acc_items: dict[str, Any] = {}
                
                async for event in conn:
                    # Handle user interruption - but with echo protection
                    if event.type == "input_audio_buffer.speech_started":
                        # Check if this might be echo from AI audio
                        current_time = time.time()
                        time_since_ai_stopped = current_time - self.ai_speech_end_time
                        
                        # If AI was just speaking, ignore this (probably echo)
                        if self.ai_speaking or time_since_ai_stopped < self.ECHO_COOLDOWN:
                            if self.verbose:
                                print(f"[ECHO] Ignored speech detection (AI active or cooldown)", end="\r")
                            continue
                        
                        # Real user interruption - cancel current response
                        self.audio_player.cancel_current()
                        self.ai_speaking = False
                        try:
                            await conn.response.cancel()
                        except:
                            pass  # No active response to cancel
                        print("\n[Interrupted] Listening...", end="\r")
                        continue
                    
                    # Response was cancelled (interrupted) - ensure audio stops
                    if event.type == "response.cancelled":
                        self.audio_player.cancel_current()
                        self.ai_speaking = False
                        self.ai_speech_end_time = time.time()
                        continue
                    
                    # Session events
                    if event.type == "session.created":
                        if self.verbose:
                            print("[INFO] Session established")
                        # Log system prompt tokens (estimate ~500 tokens for our minimal prompt)
                        self.cost_tracker.log_realtime_audio(
                            text_input_tokens=500,
                            event_type="session_init",
                            notes="System prompt"
                        )
                        continue
                    
                    if event.type == "session.updated":
                        print("\n" + "="*50)
                        print("READY - Start speaking into your microphone")
                        print("="*50 + "\n")
                        continue
                    
                    # Audio output from AI - queue for playback and mark AI as speaking
                    if event.type in ("response.audio.delta", "response.output_audio.delta"):
                        self.ai_speaking = True
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
                        # AI finished speaking - mark end time for echo protection
                        self.ai_speaking = False
                        self.ai_speech_end_time = time.time()
                        
                        # Print the complete transcript once at the end
                        try:
                            item_id = getattr(event, 'item_id', 'default')
                            if item_id in acc_items:
                                ai_response = acc_items[item_id]
                                print(f"Assistant: {ai_response}")
                                
                                # Log cost for this turn
                                # Estimate: ~150 chars/sec speech, so chars/150 = seconds
                                audio_out_seconds = len(ai_response) / 15  # ~15 chars per second for speech
                                audio_in_seconds = 3  # Estimate user spoke ~3 seconds
                                
                                self.cost_tracker.log_realtime_audio(
                                    audio_input_seconds=audio_in_seconds,
                                    audio_output_seconds=audio_out_seconds,
                                    text_output_tokens=len(ai_response) // 4,  # ~4 chars per token
                                    event_type="conversation_turn",
                                    notes=ai_response[:50] + "..." if len(ai_response) > 50 else ai_response
                                )
                                
                                # Print running cost
                                self.cost_tracker.print_live_cost()
                                
                                # Track for summarization
                                self.turn_count += 1
                                if self.recent_exchanges:
                                    self.recent_exchanges[-1]['assistant'] = ai_response
                                
                                # Check if we need to summarize
                                if self.turn_count >= self.MAX_TURNS_BEFORE_SUMMARY:
                                    await self.summarize_conversation()
                                    
                        except Exception as e:
                            pass
                        continue
                    
                    # Response completed - good place to check history size
                    if event.type == "response.done":
                        # Mark AI as done speaking (backup in case transcript.done doesn't fire)
                        self.ai_speaking = False
                        self.ai_speech_end_time = time.time()
                        # Truncate if conversation is getting too long
                        await self.truncate_old_items()
                        continue
                    
                    # User speech detected (no transcript since we disabled Whisper)
                    if event.type == "input_audio_buffer.speech_stopped":
                        # Track that user said something (we don't have text without Whisper)
                        self.recent_exchanges.append({'user': '[audio]', 'assistant': ''})
                        # Start timing for this turn
                        self.turn_start_time = time.time()
                        print("[Processing...]", end="\r")
                        continue
                    
                    # ===== TOOL/FUNCTION CALLING =====
                    # When the model wants to call a tool, handle it and send result back
                    if event.type == "response.function_call_arguments.done":
                        try:
                            tool_name = event.name
                            call_id = event.call_id
                            arguments = json.loads(event.arguments) if event.arguments else {}
                            
                            if self.verbose:
                                print(f"[TOOL] {tool_name}({arguments})")
                            
                            # Execute the tool
                            result = handle_tool_call(tool_name, arguments)
                            
                            # Log tool call (no direct cost, but track usage)
                            self.cost_tracker.log_tool_call(
                                tool_name=tool_name,
                                output_tokens=len(result) // 4  # Tool output becomes input tokens
                            )
                            
                            # Send result back to the model
                            await conn.conversation.item.create(
                                item={
                                    "type": "function_call_output",
                                    "call_id": call_id,
                                    "output": result
                                }
                            )
                            
                            # Trigger model to continue with the tool result
                            await conn.response.create()
                            
                        except Exception as e:
                            if self.verbose:
                                print(f"[ERROR] Tool error: {e}")
                        continue
                    
                    # Error handling
                    if event.type == "error":
                        error_msg = str(getattr(event, 'error', event))
                        # Suppress cancel errors (normal during interruptions)
                        if 'response_cancel_not_active' not in error_msg:
                            print(f"\n[ERROR] API: {error_msg}")
                        continue
                        
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"\n[ERROR] Connection error: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
    
    async def run_async(self):
        """Main async entry point"""
        print(f"\n{'='*60}")
        print(f"  {HOSPITAL_NAME.upper()} VOICE ASSISTANT")
        print(f"{'='*60}")
        print("\nSpeak into your microphone to ask about:")
        print("   - Doctors and availability")
        print("   - Department information") 
        print("   - Hospital facilities and timings")
        print("   - Which specialist for your symptoms")
        print("\nPress Ctrl+C to stop")
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
            # End cost tracking session and print summary
            self.cost_tracker.end_session()
            print("\nVoice agent stopped.")
    
    def run(self):
        """Synchronous entry point - runs the async event loop"""
        try:
            asyncio.run(self.run_async())
        except KeyboardInterrupt:
            # Still end the session on keyboard interrupt
            self.cost_tracker.end_session()
            print("\n\nGoodbye! Thank you for using our voice assistant.")


class VoiceAgent:
    """
    Legacy VoiceAgent class for backward compatibility.
    Wraps the RealtimeVoiceAgent.
    """
    
    def __init__(self, verbose: bool = False, speech_recognition=None, text_to_speech=None, query_handler=None):
        self.realtime_agent = RealtimeVoiceAgent(verbose=verbose)
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
    agent.run()