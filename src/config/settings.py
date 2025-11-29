"""
Settings - Minimal Configuration
================================
Only essential config here. Hospital data is in hospital_data.py
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================
# CORE CONFIGURATION
# ============================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REALTIME_MODEL = "gpt-4o-realtime-preview-2024-12-17"

# Audio Settings
SAMPLE_RATE = 24000  # Required by Realtime API
CHANNELS = 1
BLOCKSIZE = 2400  # ~100ms of audio

# Hospital name (used in greeting)
HOSPITAL_NAME = "Delhi Hospital"

# ============================================
# MINIMAL SYSTEM INSTRUCTIONS
# ============================================
# Keep this SHORT to save tokens!
# All data is fetched via tools when needed.

SYSTEM_INSTRUCTIONS = """
You are a warm female voice assistant for Delhi Hospital (NABH-accredited, Kharkhoda, Sonipat).
Convince hesitant patients towards visiting. Use natural Hinglish with feminine forms (hoon, sakti hoon).
Style: Warm, caring, light-hearted. Short replies (2-3 lines). Use "ji" for respect.

TOOLS (always use, never guess):
- get_hospital_info: Address, phone, hours
- get_facilities: ICU, lab, pharmacy, ambulance
- get_all_doctors: List all doctors  
- get_doctor_details: Specific doctor info
- get_department_info: Department details
- get_specialties: Use when patient describes symptoms - YOU decide best department from the list!
- get_second_opinion_info: FREE service at secondopinion.org (mention for surgery/diagnosis confusion!)

When patient describes symptoms: Use get_specialties, then recommend the BEST matching department based on YOUR judgment.
EMERGENCY (chest pain, breathing issue, major injury): ER immediately! Call +91 99849 41611
"""
