"""
Cost Tracker - Logs all API usage with token counts and estimated costs
========================================================================
Stores logs in JSON format for easy analysis.
Supports verbose mode for detailed output.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional
import threading

# Pricing as of Nov 2024 (update these as OpenAI changes prices)
PRICING = {
    # Realtime API (gpt-4o-realtime)
    "gpt-4o-realtime-preview-2024-12-17": {
        "audio_input_per_min": 0.06,      # $0.06 per minute of audio input
        "audio_output_per_min": 0.24,     # $0.24 per minute of audio output  
        "text_input_per_1k": 0.005,       # $5 per 1M input tokens
        "text_output_per_1k": 0.02,       # $20 per 1M output tokens
    },
    # Chat models
    "gpt-4o": {
        "input_per_1k": 0.0025,           # $2.50 per 1M
        "output_per_1k": 0.01,            # $10 per 1M
    },
    "gpt-4o-mini": {
        "input_per_1k": 0.00015,          # $0.15 per 1M
        "output_per_1k": 0.0006,          # $0.60 per 1M
    },
}


class CostTracker:
    """
    Tracks API usage and costs, saves to JSON log file.
    Thread-safe for use in async applications.
    Supports verbose mode for detailed console output.
    """
    
    def __init__(self, log_dir: str = None, verbose: bool = False):
        """
        Initialize the cost tracker.
        
        Args:
            log_dir: Directory to store logs. Defaults to 'logs' in project root.
            verbose: If True, print detailed cost information to console.
        """
        self.verbose = verbose
        
        if log_dir is None:
            project_root = Path(__file__).parent.parent.parent
            log_dir = project_root / "logs"
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Current session tracking
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        # Human-readable filename: session_2025-11-29_at_19-45-30.json
        readable_timestamp = self.session_start.strftime("%Y-%m-%d_at_%H-%M-%S")
        
        # Aggregated stats by model
        self.model_stats = {}
        
        # In-memory stats for current session
        self.session_stats = {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "end_time": None,
            "total_cost": 0.0,
            "model_breakdown": {},
            "entries": []
        }
        
        # Thread lock for safe concurrent writes
        self._lock = threading.Lock()
        
        # File paths - human readable timestamp
        self.session_log_file = self.log_dir / f"session_{readable_timestamp}.json"
        self.summary_file = self.log_dir / "usage_summary.json"
        
        if self.verbose:
            print(f"[COST] Tracker initialized. Logs: {self.log_dir}")
    
    def _update_model_stats(self, model: str, cost: float, usage: dict):
        """Update aggregated stats for a model."""
        if model not in self.model_stats:
            self.model_stats[model] = {
                "calls": 0,
                "total_cost": 0.0,
                "audio_input_sec": 0,
                "audio_output_sec": 0,
                "text_input_tokens": 0,
                "text_output_tokens": 0,
            }
        
        stats = self.model_stats[model]
        stats["calls"] += 1
        stats["total_cost"] += cost
        stats["audio_input_sec"] += usage.get("audio_input_seconds", 0)
        stats["audio_output_sec"] += usage.get("audio_output_seconds", 0)
        stats["text_input_tokens"] += usage.get("input_tokens", 0) + usage.get("text_input_tokens", 0)
        stats["text_output_tokens"] += usage.get("output_tokens", 0) + usage.get("text_output_tokens", 0)
    
    def log_realtime_audio(
        self,
        audio_input_seconds: float = 0,
        audio_output_seconds: float = 0,
        text_input_tokens: int = 0,
        text_output_tokens: int = 0,
        model: str = "gpt-4o-realtime-preview-2024-12-17",
        event_type: str = "conversation_turn",
        notes: str = ""
    ):
        """Log Realtime API audio usage."""
        pricing = PRICING.get(model, PRICING["gpt-4o-realtime-preview-2024-12-17"])
        
        # Calculate costs
        audio_in_cost = (audio_input_seconds / 60) * pricing["audio_input_per_min"]
        audio_out_cost = (audio_output_seconds / 60) * pricing["audio_output_per_min"]
        text_in_cost = (text_input_tokens / 1000) * pricing["text_input_per_1k"]
        text_out_cost = (text_output_tokens / 1000) * pricing["text_output_per_1k"]
        total_cost = audio_in_cost + audio_out_cost + text_in_cost + text_out_cost
        
        usage = {
            "audio_input_seconds": round(audio_input_seconds, 2),
            "audio_output_seconds": round(audio_output_seconds, 2),
            "text_input_tokens": text_input_tokens,
            "text_output_tokens": text_output_tokens,
        }
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "type": "realtime_audio",
            "event": event_type,
            "usage": usage,
            "cost": {
                "audio_input": round(audio_in_cost, 6),
                "audio_output": round(audio_out_cost, 6),
                "text_input": round(text_in_cost, 6),
                "text_output": round(text_out_cost, 6),
                "total": round(total_cost, 6),
            },
            "notes": notes
        }
        
        self._add_entry(entry, model, total_cost, usage)
        return total_cost
    
    def log_chat_completion(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        purpose: str = "chat"
    ):
        """Log chat completion API usage (GPT-4o, GPT-4o-mini, etc.)"""
        pricing = PRICING.get(model, PRICING["gpt-4o-mini"])
        
        in_cost = (input_tokens / 1000) * pricing["input_per_1k"]
        out_cost = (output_tokens / 1000) * pricing["output_per_1k"]
        total_cost = in_cost + out_cost
        
        usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "type": "chat_completion",
            "event": purpose,
            "usage": usage,
            "cost": {
                "input": round(in_cost, 6),
                "output": round(out_cost, 6),
                "total": round(total_cost, 6),
            }
        }
        
        self._add_entry(entry, model, total_cost, usage)
        return total_cost
    
    def log_tool_call(self, tool_name: str, input_tokens: int = 0, output_tokens: int = 0):
        """Log a tool/function call (part of realtime, no extra cost but useful to track)."""
        usage = {"input_tokens": input_tokens, "output_tokens": output_tokens}
        entry = {
            "timestamp": datetime.now().isoformat(),
            "model": "tool_call",
            "type": "function_call",
            "event": tool_name,
            "usage": usage,
            "cost": {"total": 0}
        }
        
        self._add_entry(entry, "tool_call", 0, usage)
        return 0
    
    def _add_entry(self, entry: dict, model: str, cost: float, usage: dict):
        """Add entry to session stats (thread-safe)."""
        with self._lock:
            self.session_stats["entries"].append(entry)
            self.session_stats["total_cost"] += cost
            self._update_model_stats(model, cost, usage)
            self._save_session()
    
    def _save_session(self):
        """Save current session to JSON file."""
        try:
            # Update model breakdown in session stats
            self.session_stats["model_breakdown"] = {
                model: {
                    "calls": stats["calls"],
                    "cost": round(stats["total_cost"], 6),
                    "audio_in_sec": round(stats["audio_input_sec"], 2),
                    "audio_out_sec": round(stats["audio_output_sec"], 2),
                    "tokens_in": stats["text_input_tokens"],
                    "tokens_out": stats["text_output_tokens"],
                }
                for model, stats in self.model_stats.items()
            }
            
            with open(self.session_log_file, 'w') as f:
                json.dump(self.session_stats, f, indent=2)
        except Exception as e:
            if self.verbose:
                print(f"[WARN] Failed to save cost log: {e}")
    
    def end_session(self):
        """Mark session as ended and update summary."""
        with self._lock:
            self.session_stats["end_time"] = datetime.now().isoformat()
            self._save_session()
            self._update_summary()
        
        if self.verbose:
            self._print_session_summary()
    
    def _print_session_summary(self):
        """Print detailed session summary (only in verbose mode)."""
        print(f"\n{'='*60}")
        print(f"  SESSION COST SUMMARY")
        print(f"{'='*60}")
        print(f"  Session ID: {self.session_id}")
        print(f"  Duration: {self._get_duration()}")
        print(f"  Total API Calls: {len(self.session_stats['entries'])}")
        print(f"{'='*60}")
        
        # Print per-model breakdown
        print(f"  MODEL BREAKDOWN:")
        print(f"  {'-'*56}")
        for model, stats in self.model_stats.items():
            if stats["total_cost"] > 0 or stats["calls"] > 0:
                print(f"  {model}:")
                print(f"    Calls: {stats['calls']}")
                if stats["audio_input_sec"] > 0:
                    print(f"    Audio In: {stats['audio_input_sec']:.1f}s")
                if stats["audio_output_sec"] > 0:
                    print(f"    Audio Out: {stats['audio_output_sec']:.1f}s")
                if stats["text_input_tokens"] > 0:
                    print(f"    Tokens In: {stats['text_input_tokens']}")
                if stats["text_output_tokens"] > 0:
                    print(f"    Tokens Out: {stats['text_output_tokens']}")
                print(f"    Cost: ${stats['total_cost']:.4f}")
                print()
        
        print(f"  {'-'*56}")
        print(f"  TOTAL SESSION COST: ${self.session_stats['total_cost']:.4f}")
        print(f"  Log saved: {self.session_log_file}")
        print(f"{'='*60}\n")
    
    def _get_duration(self) -> str:
        """Get session duration as formatted string."""
        if self.session_stats["end_time"]:
            end = datetime.fromisoformat(self.session_stats["end_time"])
            duration = end - self.session_start
            minutes = int(duration.total_seconds() // 60)
            seconds = int(duration.total_seconds() % 60)
            return f"{minutes}m {seconds}s"
        return "ongoing"
    
    def _update_summary(self):
        """Update the overall usage summary file."""
        summary = {"sessions": [], "total_cost_all_time": 0}
        
        if self.summary_file.exists():
            try:
                with open(self.summary_file) as f:
                    summary = json.load(f)
            except:
                pass
        
        session_summary = {
            "session_id": self.session_id,
            "date": self.session_start.strftime("%Y-%m-%d"),
            "start": self.session_stats["start_time"],
            "end": self.session_stats["end_time"],
            "entries": len(self.session_stats["entries"]),
            "cost": round(self.session_stats["total_cost"], 4),
            "model_breakdown": self.session_stats.get("model_breakdown", {})
        }
        
        summary["sessions"].append(session_summary)
        summary["total_cost_all_time"] = round(
            sum(s["cost"] for s in summary["sessions"]), 4
        )
        
        try:
            with open(self.summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
        except Exception as e:
            if self.verbose:
                print(f"[WARN] Failed to update summary: {e}")
    
    def get_session_cost(self) -> float:
        """Get current session's total cost."""
        return self.session_stats["total_cost"]
    
    def print_live_cost(self):
        """Print current cost (only in verbose mode)."""
        if self.verbose:
            cost = self.session_stats["total_cost"]
            entries = len(self.session_stats["entries"])
            print(f"[COST] ${cost:.4f} ({entries} calls)", end="\r")


# Global instance for easy access
_tracker: Optional[CostTracker] = None
_verbose: bool = False


def get_tracker() -> CostTracker:
    """Get or create the global cost tracker."""
    global _tracker
    if _tracker is None:
        _tracker = CostTracker(verbose=_verbose)
    return _tracker


def init_tracker(log_dir: str = None, verbose: bool = False) -> CostTracker:
    """Initialize a new cost tracker."""
    global _tracker, _verbose
    _verbose = verbose
    _tracker = CostTracker(log_dir, verbose=verbose)
    return _tracker
