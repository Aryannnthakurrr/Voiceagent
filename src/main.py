#!/usr/bin/env python3
"""
Hospital Voice Agent - Main Entry Point

A real-time AI voice assistant for hospital inquiries using OpenAI's Realtime API.
Run this script to start a live voice conversation.

Usage:
    python main.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.voice_agent import VoiceAgent
from config.settings import OPENAI_API_KEY


def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    
    try:
        import openai
    except ImportError:
        missing.append("openai")
    
    try:
        import sounddevice
    except ImportError:
        missing.append("sounddevice")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing.append("python-dotenv")
    
    if missing:
        print("❌ Missing dependencies. Please install them:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True


def check_api_key():
    """Check if OpenAI API key is configured"""
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured!")
        print("   Please set your API key in the .env file:")
        print("   OPENAI_API_KEY=your_key_here")
        return False
    return True


def check_audio_devices():
    """Check if audio input/output devices are available"""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        input_device = sd.query_devices(kind='input')
        output_device = sd.query_devices(kind='output')
        
        print(f"🎤 Input device: {input_device['name']}")
        print(f"🔊 Output device: {output_device['name']}")
        return True
    except Exception as e:
        print(f"❌ Audio device error: {e}")
        print("   Please ensure you have a microphone and speakers connected.")
        return False


def main():
    """Main entry point for the voice agent"""
    print("\n🏥 Hospital Voice Agent - Startup Check")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        sys.exit(1)
    
    # Check audio devices
    if not check_audio_devices():
        sys.exit(1)
    
    print("=" * 50)
    print("✅ All checks passed! Starting voice agent...\n")
    
    # Start the voice agent
    voice_agent = VoiceAgent()
    voice_agent.listen_and_respond()


if __name__ == "__main__":
    main()