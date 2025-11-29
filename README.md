# Hospital Voice Agent

A real-time AI voice assistant for hospital patient inquiries using OpenAI's Realtime API. The agent handles live voice conversations in Hinglish (Hindi-English), providing information about doctors, departments, facilities, and symptom-based recommendations.

## Features

- **Real-time Voice Conversation** - Full-duplex audio using OpenAI's GPT-4o Realtime API
- **Natural Language Understanding** - Understands Hindi, English, and Hinglish
- **Smart Symptom Routing** - AI recommends the best department based on patient symptoms
- **Function Calling** - Uses tools to fetch hospital data on-demand (reduces costs)
- **Conversation Summarization** - Compresses history using GPT-4o-mini to manage token usage
- **Cost Tracking** - Logs all API usage with detailed cost breakdown
- **Interrupt Support** - Users can interrupt the AI mid-response (barge-in)

## Requirements

- Python 3.9+
- OpenAI API key with Realtime API access
- Microphone and speakers
- Windows, macOS, or Linux

## Installation

1. **Clone or navigate to the project:**
   ```bash
   cd hospital-voice-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API key:**
   
   Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Run the agent:**
   ```bash
   cd src
   python main.py
   ```

## Usage

### Basic Mode
```bash
python main.py
```
Runs with minimal console output. Cost tracking happens in background.

### Verbose Mode
```bash
python main.py --verbose
```
Shows detailed output including:
- Audio device information
- Tool calls and their results
- Real-time cost tracking
- Session summary with per-model breakdown

### During Conversation
- Speak naturally into your microphone
- Interrupt the AI at any time by speaking
- Press `Ctrl+C` to stop

### Example Questions
- "I have knee pain, which doctor should I see?"
- "What are the hospital timings?"
- "Tell me about Dr. Anil Sharma"
- "Kya facilities hain hospital mein?"
- "I was advised surgery, should I get a second opinion?"

## Project Structure

```
hospital-voice-agent/
├── src/
│   ├── main.py                 # Entry point
│   ├── agent/
│   │   ├── voice_agent.py      # Core realtime voice agent
│   │   └── tools.py            # Function definitions for API
│   ├── config/
│   │   ├── settings.py         # Configuration & system prompt
│   │   └── hospital_data.py    # Hospital information & data functions
│   └── utils/
│       ├── audio_utils.py      # Audio helpers
│       └── cost_tracker.py     # Usage logging & cost calculation
├── logs/                       # Session logs (JSON)
├── tests/
├── requirements.txt
├── pyproject.toml
└── .env                        # API key (not committed)
```

## Configuration

### System Prompt
Edit `src/config/settings.py` to customize the AI's personality and behavior.

### Hospital Data
Edit `src/config/hospital_data.py` to update:
- Hospital information (address, phones, hours)
- Doctors and departments
- Facilities list
- Second opinion service details

### Cost Tracking
Logs are saved to `logs/` directory:
- `session_YYYYMMDD_HHMMSS.json` - Per-session detailed logs
- `usage_summary.json` - Aggregate usage across all sessions

## Tools (Function Calling)

The agent uses 7 tools to fetch data on-demand:

| Tool | Description |
|------|-------------|
| `get_hospital_info` | Address, phone, hours |
| `get_facilities` | List of hospital services |
| `get_all_doctors` | Summary of all doctors |
| `get_doctor_details` | Specific doctor information |
| `get_department_info` | Department details |
| `get_specialties` | All departments for symptom routing |
| `get_second_opinion_info` | Free second opinion service |

## Cost Optimization

This implementation includes several cost-saving measures:

1. **Minimal System Prompt** - ~320 tokens instead of embedding all data
2. **On-demand Data Fetching** - Tools fetch only what's needed
3. **Conversation Summarization** - Compresses history after 4 turns using GPT-4o-mini
4. **No Whisper Transcription** - Uses Realtime API's built-in speech recognition

Estimated cost: ~$0.25-0.35 per 3-minute conversation

## Troubleshooting

**No audio input:**
- Check microphone permissions in system settings
- Verify microphone is set as default input device

**API errors:**
- Ensure your API key has Realtime API access
- Check your OpenAI account has sufficient credits

**Audio playback issues:**
- Verify speakers/headphones are connected
- Check audio output device in system settings

## License

MIT License