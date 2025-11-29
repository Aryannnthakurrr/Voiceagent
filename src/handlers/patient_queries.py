"""
Patient Queries Handler for Hospital Voice Agent
Maps symptoms to departments and provides guidance
"""


class SymptomMapper:
    """Maps patient symptoms to appropriate departments"""
    
    SYMPTOM_MAPPINGS = {
        # Orthopedics
        "orthopedics": [
            "bone pain", "joint pain", "fracture", "broken bone", "sprain",
            "back pain", "spine", "knee pain", "hip pain", "shoulder pain",
            "sports injury", "arthritis", "muscle pain", "stiffness"
        ],
        # Cardiology
        "cardiology": [
            "chest pain", "heart", "palpitations", "blood pressure", "hypertension",
            "shortness of breath", "breathing difficulty", "dizziness", "fainting",
            "irregular heartbeat", "heart attack"
        ],
        # General Medicine
        "general_medicine": [
            "fever", "cold", "cough", "flu", "headache", "fatigue",
            "weakness", "diabetes", "infection", "general checkup",
            "body ache", "nausea", "vomiting", "stomach pain"
        ],
        # Dermatology
        "dermatology": [
            "skin", "rash", "acne", "pimples", "itching", "allergy",
            "hair loss", "eczema", "psoriasis", "fungal", "skin infection"
        ],
        # Pediatrics
        "pediatrics": [
            "child", "baby", "infant", "kid", "vaccination", "immunization",
            "growth", "developmental"
        ],
        # ENT
        "ent": [
            "ear pain", "hearing", "deaf", "nose", "sinus", "nasal",
            "throat", "tonsils", "voice", "snoring", "sleep apnea"
        ]
    }
    
    DEPARTMENT_DOCTORS = {
        "orthopedics": ["Dr. Sarah Johnson", "Dr. Michael Chen"],
        "cardiology": ["Dr. Emily Williams", "Dr. Robert Kumar"],
        "general_medicine": ["Dr. Lisa Anderson", "Dr. James Wilson"],
        "dermatology": ["Dr. Priya Sharma"],
        "pediatrics": ["Dr. Amanda Brown"],
        "ent": ["Dr. David Lee"]
    }
    
    @classmethod
    def find_department(cls, symptoms: str) -> tuple:
        """
        Find the most appropriate department based on symptoms.
        Returns (department_name, confidence_keywords)
        """
        symptoms_lower = symptoms.lower()
        matches = {}
        
        for department, keywords in cls.SYMPTOM_MAPPINGS.items():
            matching_keywords = [kw for kw in keywords if kw in symptoms_lower]
            if matching_keywords:
                matches[department] = matching_keywords
        
        if not matches:
            return None, []
        
        # Return department with most keyword matches
        best_match = max(matches.items(), key=lambda x: len(x[1]))
        return best_match[0], best_match[1]
    
    @classmethod
    def get_doctors_for_department(cls, department: str) -> list:
        """Get doctors for a specific department"""
        return cls.DEPARTMENT_DOCTORS.get(department.lower(), [])


class PatientQueriesHandler:
    """Handles patient-related queries"""
    
    def __init__(self):
        self.symptom_mapper = SymptomMapper()
    
    def handle_query(self, query: str) -> str:
        """Process the patient-related query and return a response"""
        response = self.process_query(query)
        return response

    def process_query(self, query: str) -> str:
        """Process query and provide appropriate guidance"""
        query_lower = query.lower()
        
        # Check for emergency keywords
        emergency_keywords = ["emergency", "severe", "accident", "unconscious", 
                            "bleeding heavily", "heart attack", "stroke", "can't breathe"]
        if any(kw in query_lower for kw in emergency_keywords):
            return ("This sounds like an emergency. Please go to our Emergency Room immediately "
                   "or call (555) 123-4567 for emergency services. Our ER is open 24/7.")
        
        # Try to find appropriate department based on symptoms
        department, keywords = self.symptom_mapper.find_department(query)
        
        if department:
            doctors = self.symptom_mapper.get_doctors_for_department(department)
            doctors_str = " or ".join(doctors)
            return (f"Based on your symptoms, I recommend visiting our {department.replace('_', ' ').title()} "
                   f"department. You can see {doctors_str}. Would you like to know their available timings?")
        
        # Default response if no match
        return ("I'd recommend starting with our General Medicine department for an initial consultation. "
               "Dr. Lisa Anderson is available Mon-Sat, 8 AM - 2 PM, or Dr. James Wilson from 2 PM - 8 PM.")
    
    def get_symptom_guidance(self, symptom: str) -> dict:
        """Get detailed guidance for a specific symptom"""
        department, keywords = self.symptom_mapper.find_department(symptom)
        
        if department:
            return {
                "recommended_department": department.replace("_", " ").title(),
                "matched_symptoms": keywords,
                "doctors": self.symptom_mapper.get_doctors_for_department(department)
            }
        return None