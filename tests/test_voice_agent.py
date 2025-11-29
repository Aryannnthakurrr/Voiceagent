import unittest
from src.agent.voice_agent import VoiceAgent

class TestVoiceAgent(unittest.TestCase):

    def setUp(self):
        self.agent = VoiceAgent()

    def test_listen(self):
        # Test the listen method
        result = self.agent.listen()
        self.assertIsInstance(result, str)  # Assuming listen returns a string

    def test_respond(self):
        # Test the respond method
        query = "What are the visiting hours?"
        response = self.agent.respond(query)
        self.assertIsInstance(response, str)  # Assuming respond returns a string
        self.assertNotEqual(response, "")  # Ensure response is not empty

if __name__ == '__main__':
    unittest.main()