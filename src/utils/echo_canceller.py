"""
Software Echo Cancellation for Mac
Uses correlation-based detection to filter out AI playback from mic input.
This prevents the AI's own audio from triggering VAD (Voice Activity Detection).
"""

import numpy as np
from collections import deque
import threading


class EchoCanceller:
    """
    Simple but effective echo cancellation.
    
    Works by:
    1. Storing recent audio that was played through speakers
    2. When mic input arrives, checking if it correlates with speaker output
    3. If correlation is high, it's echo - suppress/ignore it
    
    This is simpler than full AEC but works well for our use case.
    """
    
    def __init__(self, sample_rate: int = 24000, buffer_seconds: float = 2.0):
        self.sample_rate = sample_rate
        self.buffer_size = int(sample_rate * buffer_seconds)
        
        # Circular buffer of recent speaker output (what AI is saying)
        self.speaker_buffer = deque(maxlen=self.buffer_size)
        
        # Lock for thread safety
        self.lock = threading.Lock()
        
        # Thresholds for echo detection (tuned to allow barge-in)
        self.correlation_threshold = 0.6  # Higher = stricter (only block clear echo)
        self.barge_in_energy_multiplier = 2.5  # If mic is 2.5x louder than speaker, it's barge-in
        
        # State tracking
        self.is_playing = False
        self.last_play_time = 0
        self.cooldown_samples = int(sample_rate * 0.3)  # Shorter 300ms cooldown
        self.samples_since_play = self.cooldown_samples + 1  # Start as "not playing"
        
    def add_speaker_audio(self, audio: np.ndarray):
        """
        Called when audio is played through speakers.
        Stores it for later comparison with mic input.
        """
        with self.lock:
            self.is_playing = True
            self.samples_since_play = 0
            
            # Add samples to buffer
            for sample in audio.flatten():
                self.speaker_buffer.append(sample)
    
    def mark_playback_stopped(self):
        """Called when AI stops speaking"""
        with self.lock:
            self.is_playing = False
    
    def process_mic_input(self, mic_audio: np.ndarray) -> tuple[np.ndarray, bool]:
        """
        Process microphone input and detect if it's echo.
        
        Returns:
            tuple: (processed_audio, is_likely_human)
            - processed_audio: The audio (possibly filtered)
            - is_likely_human: True if this seems like real human speech, False if echo
        """
        with self.lock:
            self.samples_since_play += len(mic_audio)
            
            # If we haven't played anything recently, it's definitely human
            if self.samples_since_play > self.cooldown_samples and not self.is_playing:
                return mic_audio, True
            
            # Calculate mic energy
            mic_energy = np.sqrt(np.mean(mic_audio.astype(np.float32) ** 2))
            
            # If very quiet, might be background noise during playback - allow it
            if mic_energy < 100:
                return mic_audio, True
            
            # Get recent speaker audio for comparison
            if len(self.speaker_buffer) < len(mic_audio):
                # Not enough speaker audio to compare - assume human
                return mic_audio, True
            
            # Compare with recent speaker output
            speaker_recent = np.array(list(self.speaker_buffer)[-len(mic_audio):])
            speaker_energy = np.sqrt(np.mean(speaker_recent.astype(np.float32) ** 2))
            
            # CRITICAL: If mic is significantly louder than speaker, it's BARGE-IN
            # User speaking over AI should be much louder than echo
            if speaker_energy > 100:
                energy_ratio = mic_energy / (speaker_energy + 1e-6)
                
                # If mic is much louder, definitely human (barge-in)
                if energy_ratio > self.barge_in_energy_multiplier:
                    return mic_audio, True
                
                # If mic is much quieter, likely background noise
                if energy_ratio < 0.3:
                    return mic_audio, True
                
                # Only block if energy is suspiciously similar (0.3 to 2.5x)
                # AND we're currently playing
                if not self.is_playing:
                    return mic_audio, True
            
            # Correlation check - only if energies are similar
            try:
                # Normalize for correlation
                mic_norm = mic_audio.astype(np.float32)
                speaker_norm = speaker_recent.astype(np.float32)
                
                # Simple correlation using dot product
                if np.std(mic_norm) > 0 and np.std(speaker_norm) > 0:
                    mic_norm = (mic_norm - np.mean(mic_norm)) / (np.std(mic_norm) + 1e-6)
                    speaker_norm = (speaker_norm - np.mean(speaker_norm)) / (np.std(speaker_norm) + 1e-6)
                    correlation = np.abs(np.dot(mic_norm, speaker_norm) / len(mic_norm))
                    
                    # Only block if VERY high correlation (clear echo)
                    if correlation > self.correlation_threshold:
                        # High correlation = echo
                        return mic_audio, False
            except Exception:
                pass  # If correlation fails, assume human
            
            # Default: allow through (favor false negatives over false positives)
            # Better to have some echo than block barge-in
            return mic_audio, True
    
    def is_safe_to_detect_speech(self) -> bool:
        """
        Quick check if it's safe to run VAD.
        Use this before expensive speech detection.
        """
        with self.lock:
            return self.samples_since_play > self.cooldown_samples and not self.is_playing


class SimpleEchoGate:
    """
    Even simpler approach: Just gate based on whether AI is speaking.
    Uses timing-based approach with gradual fade.
    
    This is less sophisticated but more reliable.
    """
    
    def __init__(self, sample_rate: int = 24000):
        self.sample_rate = sample_rate
        self.is_ai_speaking = False
        self.samples_since_ai_stopped = 0
        self.gate_samples = int(sample_rate * 0.6)  # 600ms gate after AI stops
        self.lock = threading.Lock()
        
    def ai_started_speaking(self):
        """Call when AI starts outputting audio"""
        with self.lock:
            self.is_ai_speaking = True
            self.samples_since_ai_stopped = 0
    
    def ai_stopped_speaking(self):
        """Call when AI finishes speaking"""
        with self.lock:
            self.is_ai_speaking = False
            self.samples_since_ai_stopped = 0
    
    def process_samples(self, num_samples: int) -> bool:
        """
        Process passage of time (in samples).
        Returns True if we should allow speech detection.
        """
        with self.lock:
            if not self.is_ai_speaking:
                self.samples_since_ai_stopped += num_samples
            
            # Allow speech detection if AI stopped long enough ago
            return not self.is_ai_speaking and self.samples_since_ai_stopped > self.gate_samples
    
    def should_send_audio(self) -> bool:
        """Check if we should send audio to API"""
        with self.lock:
            # Always send audio - let server-side VAD handle it
            # But this can be used to gate if needed
            return True
    
    def get_state(self) -> str:
        """Get current state for debugging"""
        with self.lock:
            if self.is_ai_speaking:
                return "AI_SPEAKING"
            elif self.samples_since_ai_stopped < self.gate_samples:
                return f"COOLDOWN_{self.samples_since_ai_stopped}/{self.gate_samples}"
            else:
                return "LISTENING"
