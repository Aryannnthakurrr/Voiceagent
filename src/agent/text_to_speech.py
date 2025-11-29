class TextToSpeech:
    def __init__(self, tts_engine):
        self.tts_engine = tts_engine

    def speak(self, text):
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()