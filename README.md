# 🏥 Hospital Voice Agent

A real-time AI voice assistant for hospital patient inquiries, powered by OpenAI's Realtime API.

## ✨ Features

- **Live Voice Conversation**: Full-duplex audio - speak naturally and get instant responses
- **Real-time Speech-to-Speech**: Uses OpenAI's GPT-4o Realtime API for low-latency conversation
- **Hospital Information**: Provides details about doctors, departments, facilities, and timings
- **Symptom Guidance**: Helps patients identify which specialist to consult
- **Natural Interaction**: Conversational AI that understands context and follow-up questions

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key with Realtime API access
- Microphone and speakers

### Installation

1. **Navigate to the project directory:**
   ```bash
   cd hospital-voice-agent
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key:**
   
   The `.env` file is already configured. If you need to update it:
   ```bash
   # Edit .env file
   OPENAI_API_KEY=your_api_key_here
   ```

4. **Run the voice agent:**
   ```bash
   cd src
   python main.py
   ```

## 🎤 How to Use

1. Run the script and wait for "Listening..." message
2. Speak naturally into your microphone
3. Ask questions like:
   - "I have knee pain, which doctor should I see?"
   - "What are Dr. Sarah Johnson's timings?"
   - "What facilities does the hospital have?"
   - "I need to see a heart specialist"
   - "What are the consultation fees?"
4. Press `Ctrl+C` to stop

## 📁 Project Structure

```
hospital-voice-agent/
├── src/
│   ├── main.py                 # Entry point - run this!
│   ├── agent/
│   │   └── voice_agent.py      # Core realtime voice agent
│   ├── config/
│   │   └── settings.py         # Configuration & hospital data
│   ├── handlers/
│   │   ├── patient_queries.py  # Symptom to department mapping
│   │   ├── general_info.py     # Hospital information
│   │   └── appointment_handler.py
│   ├── services/
│   │   ├── llm_service.py
│   │   └── patient_data_service.py
│   └── utils/
│       └── audio_utils.py
├── tests/
├── requirements.txt
├── .env                        # Your API key (do not commit!)
└── README.md
```

## 🏥 Demo Hospital Data

The agent is configured with demo data for "City General Hospital":

### Departments & Doctors

| Department | Doctors | Hours | Fee |
|------------|---------|-------|-----|
| Orthopedics | Dr. Sarah Johnson | Mon, Wed, Fri: 9-5 | $150 |
| Orthopedics | Dr. Michael Chen | Tue, Thu: 10-6 | $175 |
| Cardiology | Dr. Emily Williams | Mon-Fri: 9-4 | $200 |
| Cardiology | Dr. Robert Kumar | Mon, Wed, Fri: 11-7 | $250 |
| General Medicine | Dr. Lisa Anderson | Mon-Sat: 8-2 | $100 |
| Dermatology | Dr. Priya Sharma | Tue, Thu, Sat: 10-5 | $130 |
| Pediatrics | Dr. Amanda Brown | Mon-Fri: 9-5 | $120 |
| ENT | Dr. David Lee | Mon, Wed, Fri: 10-4 | $140 |

### Facilities
- 24/7 Emergency Room
- Advanced Diagnostic Lab
- Digital X-Ray & MRI
- 24-hour Pharmacy
- Ambulance Service
- ICU (20 beds)
- Private & Semi-private rooms

## ⚙️ Configuration

Edit `src/config/settings.py` to customize:
- Hospital information
- Department and doctor data
- System instructions for the AI
- Audio settings

## 🔧 Troubleshooting

**No audio input detected:**
- Check microphone permissions
- Ensure microphone is set as default input device

**API errors:**
- Verify your OpenAI API key is correct
- Ensure you have access to the Realtime API

**Audio playback issues:**
- Check speaker/headphone connection
- Ensure audio output device is configured

## 📝 License

MIT License

## License
This project is licensed under the MIT License. See the LICENSE file for details.