import unittest
from src.handlers.patient_queries import PatientQueriesHandler
from src.handlers.appointment_handler import AppointmentHandler
from src.handlers.general_info import GeneralInfoHandler

class TestPatientQueriesHandler(unittest.TestCase):
    def setUp(self):
        self.handler = PatientQueriesHandler()

    def test_handle_query(self):
        response = self.handler.handle_query("What are the visiting hours?")
        self.assertIn("visiting hours", response.lower())

class TestAppointmentHandler(unittest.TestCase):
    def setUp(self):
        self.handler = AppointmentHandler()

    def test_schedule_appointment(self):
        response = self.handler.schedule_appointment("2023-10-01", "10:00 AM")
        self.assertEqual(response, "Appointment scheduled for 2023-10-01 at 10:00 AM.")

    def test_cancel_appointment(self):
        response = self.handler.cancel_appointment("12345")
        self.assertEqual(response, "Appointment 12345 has been canceled.")

class TestGeneralInfoHandler(unittest.TestCase):
    def setUp(self):
        self.handler = GeneralInfoHandler()

    def test_provide_info(self):
        response = self.handler.provide_info("What services do you offer?")
        self.assertIn("services", response.lower())

if __name__ == '__main__':
    unittest.main()