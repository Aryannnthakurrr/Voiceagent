#!/usr/bin/env python3
"""
Diagnostic Script for Hospital Voice Agent
===========================================
Runs comprehensive tests to verify system health and configuration.

Usage:
    python scripts/diagnose.py          # Run all tests
    python scripts/diagnose.py --quick  # Skip slow tests
    python scripts/diagnose.py --api    # Include API connectivity test
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add src to path
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))


class DiagnosticRunner:
    """Runs diagnostic tests and reports results."""
    
    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0
    
    def log(self, status: str, test_name: str, message: str = ""):
        """Log a test result."""
        icons = {"PASS": "[OK]", "FAIL": "[FAIL]", "WARN": "[WARN]", "INFO": "[INFO]"}
        icon = icons.get(status, "[??]")
        
        result = {"status": status, "test": test_name, "message": message}
        self.results.append(result)
        
        if status == "PASS":
            self.passed += 1
        elif status == "FAIL":
            self.failed += 1
        elif status == "WARN":
            self.warnings += 1
        
        msg_str = f" - {message}" if message else ""
        print(f"  {icon} {test_name}{msg_str}")
    
    def section(self, title: str):
        """Print section header."""
        print(f"\n{'='*50}")
        print(f"  {title}")
        print(f"{'='*50}")


def test_python_version(runner: DiagnosticRunner):
    """Check Python version."""
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 9:
        runner.log("PASS", "Python version", version_str)
    elif version.major >= 3:
        runner.log("WARN", "Python version", f"{version_str} (3.9+ recommended)")
    else:
        runner.log("FAIL", "Python version", f"{version_str} (need 3.9+)")


def test_dependencies(runner: DiagnosticRunner):
    """Check all required dependencies."""
    dependencies = [
        ("openai", "OpenAI SDK"),
        ("sounddevice", "Audio I/O"),
        ("numpy", "Numerical processing"),
        ("dotenv", "Environment variables"),
    ]
    
    for module, desc in dependencies:
        try:
            if module == "dotenv":
                __import__("dotenv")
            else:
                __import__(module)
            runner.log("PASS", f"Dependency: {desc}")
        except ImportError:
            runner.log("FAIL", f"Dependency: {desc}", f"pip install {module}")


def test_openai_version(runner: DiagnosticRunner):
    """Check OpenAI SDK version supports Realtime API."""
    try:
        import openai
        version = openai.__version__
        major, minor = map(int, version.split(".")[:2])
        
        if major >= 1 and minor >= 50:
            runner.log("PASS", "OpenAI SDK version", version)
        else:
            runner.log("WARN", "OpenAI SDK version", f"{version} (1.50+ recommended for Realtime)")
    except Exception as e:
        runner.log("FAIL", "OpenAI SDK version", str(e))


def test_api_key(runner: DiagnosticRunner):
    """Check API key is configured."""
    try:
        from config.settings import OPENAI_API_KEY
        
        if not OPENAI_API_KEY:
            runner.log("FAIL", "API Key", "Not set in .env file")
        elif OPENAI_API_KEY == "your_openai_api_key_here":
            runner.log("FAIL", "API Key", "Still using placeholder value")
        elif len(OPENAI_API_KEY) < 20:
            runner.log("WARN", "API Key", "Seems too short")
        else:
            masked = OPENAI_API_KEY[:8] + "..." + OPENAI_API_KEY[-4:]
            runner.log("PASS", "API Key", f"Configured ({masked})")
    except Exception as e:
        runner.log("FAIL", "API Key", str(e))


def test_audio_devices(runner: DiagnosticRunner):
    """Check audio input/output devices."""
    try:
        import sounddevice as sd
        
        # Check input device
        try:
            input_dev = sd.query_devices(kind='input')
            runner.log("PASS", "Audio input", input_dev['name'][:40])
        except Exception:
            runner.log("FAIL", "Audio input", "No input device found")
        
        # Check output device
        try:
            output_dev = sd.query_devices(kind='output')
            runner.log("PASS", "Audio output", output_dev['name'][:40])
        except Exception:
            runner.log("FAIL", "Audio output", "No output device found")
            
    except Exception as e:
        runner.log("FAIL", "Audio devices", str(e))


def test_config_imports(runner: DiagnosticRunner):
    """Test configuration imports."""
    try:
        from config.settings import (
            SYSTEM_INSTRUCTIONS,
            REALTIME_MODEL,
            SAMPLE_RATE,
            HOSPITAL_NAME
        )
        runner.log("PASS", "Config: settings.py")
        runner.log("INFO", "Hospital name", HOSPITAL_NAME)
        runner.log("INFO", "Model", REALTIME_MODEL)
        runner.log("INFO", "System prompt", f"~{len(SYSTEM_INSTRUCTIONS)} chars")
    except Exception as e:
        runner.log("FAIL", "Config: settings.py", str(e))


def test_hospital_data(runner: DiagnosticRunner):
    """Test hospital data functions."""
    try:
        from config.hospital_data import (
            get_hospital_info,
            get_facilities,
            get_all_doctors_summary,
            get_doctor_details,
            get_department_info,
            get_all_specialties_for_routing,
            get_second_opinion_info,
            DOCTORS,
            EMERGENCY_SYMPTOMS
        )
        
        runner.log("PASS", "Config: hospital_data.py")
        
        # Test each function
        tests = [
            ("get_hospital_info", get_hospital_info),
            ("get_facilities", get_facilities),
            ("get_all_doctors_summary", get_all_doctors_summary),
            ("get_all_specialties_for_routing", get_all_specialties_for_routing),
            ("get_second_opinion_info", get_second_opinion_info),
        ]
        
        for name, func in tests:
            result = func()
            if result and len(result) > 10:
                runner.log("PASS", f"Function: {name}", f"{len(result)} chars")
            else:
                runner.log("WARN", f"Function: {name}", "Empty or short response")
        
        # Test with parameters
        doc_result = get_doctor_details("Anil")
        if "Anil" in doc_result or "Doctor" in doc_result:
            runner.log("PASS", "Function: get_doctor_details", "Returns data")
        else:
            runner.log("WARN", "Function: get_doctor_details", "No match found")
        
        dept_result = get_department_info("orthopedics")
        if "Orthopedics" in dept_result or "Department" in dept_result:
            runner.log("PASS", "Function: get_department_info", "Returns data")
        else:
            runner.log("WARN", "Function: get_department_info", "No match found")
        
        # Data stats
        runner.log("INFO", "Departments", str(len(DOCTORS)))
        runner.log("INFO", "Emergency symptoms", str(len(EMERGENCY_SYMPTOMS)))
        
    except Exception as e:
        runner.log("FAIL", "Config: hospital_data.py", str(e))


def test_tools(runner: DiagnosticRunner):
    """Test tools module."""
    try:
        from agent.tools import TOOLS, handle_tool_call
        
        runner.log("PASS", "Tools: tools.py")
        runner.log("INFO", "Tool count", str(len(TOOLS)))
        
        tool_names = [t["name"] for t in TOOLS]
        expected_tools = [
            "get_hospital_info",
            "get_facilities", 
            "get_all_doctors",
            "get_doctor_details",
            "get_department_info",
            "get_specialties",
            "get_second_opinion_info"
        ]
        
        for tool in expected_tools:
            if tool in tool_names:
                runner.log("PASS", f"Tool: {tool}")
            else:
                runner.log("FAIL", f"Tool: {tool}", "Missing from TOOLS list")
        
        # Test handle_tool_call
        result = handle_tool_call("get_hospital_info", {})
        if "Hospital" in result or "Delhi" in result:
            runner.log("PASS", "handle_tool_call", "Executes correctly")
        else:
            runner.log("WARN", "handle_tool_call", "Unexpected result")
            
    except Exception as e:
        runner.log("FAIL", "Tools: tools.py", str(e))


def test_cost_tracker(runner: DiagnosticRunner):
    """Test cost tracker module."""
    try:
        from utils.cost_tracker import CostTracker, PRICING
        
        runner.log("PASS", "Utils: cost_tracker.py")
        
        # Check pricing models
        expected_models = ["gpt-4o-realtime-preview-2024-12-17", "gpt-4o", "gpt-4o-mini"]
        for model in expected_models:
            if model in PRICING:
                runner.log("PASS", f"Pricing: {model[:30]}")
            else:
                runner.log("WARN", f"Pricing: {model[:30]}", "Not in PRICING dict")
        
        # Test tracker creation (use temp dir)
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            tracker = CostTracker(log_dir=tmpdir, verbose=False)
            
            # Log some test data
            tracker.log_realtime_audio(audio_input_seconds=5, audio_output_seconds=10)
            tracker.log_chat_completion("gpt-4o-mini", 100, 50)
            tracker.log_tool_call("test_tool")
            
            cost = tracker.get_session_cost()
            if cost > 0:
                runner.log("PASS", "Cost calculation", f"${cost:.4f}")
            else:
                runner.log("WARN", "Cost calculation", "Zero cost computed")
                
    except Exception as e:
        runner.log("FAIL", "Utils: cost_tracker.py", str(e))


def test_voice_agent_import(runner: DiagnosticRunner):
    """Test voice agent can be imported."""
    try:
        from agent.voice_agent import VoiceAgent, RealtimeVoiceAgent, AudioPlayer
        runner.log("PASS", "Agent: voice_agent.py")
        runner.log("PASS", "Class: VoiceAgent")
        runner.log("PASS", "Class: RealtimeVoiceAgent")
        runner.log("PASS", "Class: AudioPlayer")
    except Exception as e:
        runner.log("FAIL", "Agent: voice_agent.py", str(e))


def test_main_import(runner: DiagnosticRunner):
    """Test main.py can be imported."""
    try:
        from main import check_dependencies, check_api_key, parse_args
        runner.log("PASS", "Main: main.py")
        runner.log("PASS", "Function: check_dependencies")
        runner.log("PASS", "Function: check_api_key")
        runner.log("PASS", "Function: parse_args")
    except Exception as e:
        runner.log("FAIL", "Main: main.py", str(e))


def test_logs_directory(runner: DiagnosticRunner):
    """Check logs directory and recent logs."""
    logs_dir = PROJECT_ROOT / "logs"
    
    if logs_dir.exists():
        runner.log("PASS", "Logs directory", str(logs_dir))
        
        # Check for log files
        session_logs = list(logs_dir.glob("session_*.json"))
        summary_file = logs_dir / "usage_summary.json"
        
        runner.log("INFO", "Session logs", str(len(session_logs)))
        
        if summary_file.exists():
            try:
                with open(summary_file) as f:
                    summary = json.load(f)
                total_cost = summary.get("total_cost_all_time", 0)
                sessions = len(summary.get("sessions", []))
                runner.log("PASS", "Usage summary", f"{sessions} sessions, ${total_cost:.4f} total")
            except Exception as e:
                runner.log("WARN", "Usage summary", f"Could not parse: {e}")
        else:
            runner.log("INFO", "Usage summary", "Not created yet")
    else:
        runner.log("WARN", "Logs directory", "Does not exist (will be created on first run)")


def test_api_connectivity(runner: DiagnosticRunner):
    """Test actual API connectivity (optional, uses tokens)."""
    try:
        from config.settings import OPENAI_API_KEY
        from openai import OpenAI
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Simple models list call (free, no tokens)
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        
        # Check for realtime model
        realtime_models = [m for m in model_ids if "realtime" in m.lower()]
        
        if realtime_models:
            runner.log("PASS", "API connectivity", "Connected to OpenAI")
            runner.log("PASS", "Realtime API access", realtime_models[0])
        else:
            runner.log("PASS", "API connectivity", "Connected to OpenAI")
            runner.log("WARN", "Realtime API access", "No realtime models found")
            
    except Exception as e:
        error_msg = str(e)
        if "insufficient_quota" in error_msg:
            runner.log("FAIL", "API connectivity", "Insufficient quota - add credits")
        elif "invalid_api_key" in error_msg:
            runner.log("FAIL", "API connectivity", "Invalid API key")
        else:
            runner.log("FAIL", "API connectivity", error_msg[:50])


def test_env_file(runner: DiagnosticRunner):
    """Check .env file exists and is configured."""
    env_file = PROJECT_ROOT / ".env"
    env_example = PROJECT_ROOT / ".env.example"
    
    if env_file.exists():
        runner.log("PASS", ".env file", "Exists")
        
        # Check it's not empty
        content = env_file.read_text().strip()
        if content:
            lines = [l for l in content.split("\n") if l.strip() and not l.startswith("#")]
            runner.log("INFO", ".env entries", str(len(lines)))
        else:
            runner.log("WARN", ".env file", "Empty")
    else:
        if env_example.exists():
            runner.log("FAIL", ".env file", "Missing - copy from .env.example")
        else:
            runner.log("FAIL", ".env file", "Missing - create with OPENAI_API_KEY=...")


def run_diagnostics(include_api: bool = False, quick: bool = False):
    """Run all diagnostic tests."""
    runner = DiagnosticRunner()
    
    print("\n" + "=" * 50)
    print("  HOSPITAL VOICE AGENT - DIAGNOSTICS")
    print("=" * 50)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Project: {PROJECT_ROOT}")
    
    # System checks
    runner.section("SYSTEM")
    test_python_version(runner)
    test_dependencies(runner)
    test_openai_version(runner)
    
    # Configuration
    runner.section("CONFIGURATION")
    test_env_file(runner)
    test_api_key(runner)
    test_config_imports(runner)
    
    # Audio (skip if quick mode)
    if not quick:
        runner.section("AUDIO")
        test_audio_devices(runner)
    
    # Modules
    runner.section("MODULES")
    test_hospital_data(runner)
    test_tools(runner)
    test_cost_tracker(runner)
    test_voice_agent_import(runner)
    test_main_import(runner)
    
    # Logs
    runner.section("LOGS")
    test_logs_directory(runner)
    
    # API (optional)
    if include_api:
        runner.section("API CONNECTIVITY")
        test_api_connectivity(runner)
    
    # Summary
    print("\n" + "=" * 50)
    print("  SUMMARY")
    print("=" * 50)
    print(f"  Passed:   {runner.passed}")
    print(f"  Failed:   {runner.failed}")
    print(f"  Warnings: {runner.warnings}")
    print("=" * 50)
    
    if runner.failed > 0:
        print("\n  [!] Some tests failed. Please fix the issues above.")
        return 1
    elif runner.warnings > 0:
        print("\n  [*] All critical tests passed with some warnings.")
        return 0
    else:
        print("\n  [+] All tests passed! System is ready.")
        return 0


def main():
    parser = argparse.ArgumentParser(description="Diagnostic tests for Hospital Voice Agent")
    parser.add_argument("--api", action="store_true", help="Include API connectivity test")
    parser.add_argument("--quick", "-q", action="store_true", help="Skip slow tests (audio)")
    args = parser.parse_args()
    
    exit_code = run_diagnostics(include_api=args.api, quick=args.quick)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
