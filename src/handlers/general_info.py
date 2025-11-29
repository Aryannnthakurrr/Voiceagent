"""
General Information Handler for Hospital Voice Agent
Provides structured hospital data for reference
"""


class HospitalData:
    """Static hospital data for the voice agent"""
    
    DEPARTMENTS = {
        "orthopedics": {
            "name": "Orthopedics",
            "description": "Bone and joint care, fractures, sports injuries",
            "doctors": ["Dr. Sarah Johnson", "Dr. Michael Chen"]
        },
        "cardiology": {
            "name": "Cardiology", 
            "description": "Heart care, ECG, blood pressure management",
            "doctors": ["Dr. Emily Williams", "Dr. Robert Kumar"]
        },
        "general_medicine": {
            "name": "General Medicine",
            "description": "General checkups, fever, infections",
            "doctors": ["Dr. Lisa Anderson", "Dr. James Wilson"]
        },
        "dermatology": {
            "name": "Dermatology",
            "description": "Skin conditions, allergies, cosmetic procedures",
            "doctors": ["Dr. Priya Sharma"]
        },
        "pediatrics": {
            "name": "Pediatrics",
            "description": "Child health, vaccinations, growth monitoring",
            "doctors": ["Dr. Amanda Brown"]
        },
        "ent": {
            "name": "ENT",
            "description": "Ear, nose, throat problems",
            "doctors": ["Dr. David Lee"]
        }
    }
    
    DOCTORS = {
        "dr_sarah_johnson": {
            "name": "Dr. Sarah Johnson",
            "department": "Orthopedics",
            "specialization": "Joint replacements, sports injuries, fractures",
            "hours": "Mon, Wed, Fri: 9 AM - 5 PM",
            "fee": 150
        },
        "dr_michael_chen": {
            "name": "Dr. Michael Chen",
            "department": "Orthopedics",
            "specialization": "Back pain, spinal surgery, disc problems",
            "hours": "Tue, Thu: 10 AM - 6 PM",
            "fee": 175
        },
        "dr_emily_williams": {
            "name": "Dr. Emily Williams",
            "department": "Cardiology",
            "specialization": "Heart disease, hypertension, ECG",
            "hours": "Mon-Fri: 9 AM - 4 PM",
            "fee": 200
        },
        "dr_robert_kumar": {
            "name": "Dr. Robert Kumar",
            "department": "Cardiology",
            "specialization": "Angioplasty, stents, heart catheterization",
            "hours": "Mon, Wed, Fri: 11 AM - 7 PM",
            "fee": 250
        },
        "dr_lisa_anderson": {
            "name": "Dr. Lisa Anderson",
            "department": "General Medicine",
            "specialization": "General checkups, fever, infections, diabetes",
            "hours": "Mon-Sat: 8 AM - 2 PM",
            "fee": 100
        },
        "dr_james_wilson": {
            "name": "Dr. James Wilson",
            "department": "Internal Medicine",
            "specialization": "Chronic conditions, preventive care",
            "hours": "Mon-Fri: 2 PM - 8 PM",
            "fee": 120
        },
        "dr_priya_sharma": {
            "name": "Dr. Priya Sharma",
            "department": "Dermatology",
            "specialization": "Skin conditions, allergies, cosmetic procedures",
            "hours": "Tue, Thu, Sat: 10 AM - 5 PM",
            "fee": 130
        },
        "dr_amanda_brown": {
            "name": "Dr. Amanda Brown",
            "department": "Pediatrics",
            "specialization": "Child health, vaccinations, growth monitoring",
            "hours": "Mon-Fri: 9 AM - 5 PM",
            "fee": 120
        },
        "dr_david_lee": {
            "name": "Dr. David Lee",
            "department": "ENT",
            "specialization": "Hearing problems, sinus, throat infections",
            "hours": "Mon, Wed, Fri: 10 AM - 4 PM",
            "fee": 140
        }
    }
    
    FACILITIES = [
        "24/7 Emergency Room",
        "Advanced Diagnostic Lab",
        "Digital X-Ray & MRI",
        "Pharmacy (Open 24 hours)",
        "Ambulance Service",
        "ICU with 20 beds",
        "Private & Semi-private rooms",
        "Cafeteria",
        "Free parking"
    ]


class GeneralInfoHandler:
    """Handler for general hospital information queries"""
    
    def __init__(self):
        self.data = HospitalData()
    
    def provide_info(self, query):
        """Provide general information based on the query."""
        query_lower = query.lower()
        
        responses = {
            "hospital hours": "Our hospital is open 24/7 for emergencies. Outpatient services are available 8 AM to 8 PM, Monday to Saturday.",
            "location": "We are located at 123 Health Street, Medical District, City 12345.",
            "address": "We are located at 123 Health Street, Medical District, City 12345.",
            "services": "We offer emergency care, outpatient services, diagnostic lab, X-Ray, MRI, pharmacy, and specialized treatments across multiple departments.",
            "contact": "You can contact us at (555) 123-4567.",
            "phone": "Our phone number is (555) 123-4567.",
            "facilities": ", ".join(self.data.FACILITIES),
            "departments": ", ".join([d["name"] for d in self.data.DEPARTMENTS.values()])
        }
        
        for key, response in responses.items():
            if key in query_lower:
                return response
        
        return "I'm sorry, I don't have that specific information. Please ask about our hours, location, services, facilities, or departments."
    
    def get_department_info(self, department_name: str) -> dict:
        """Get information about a specific department"""
        key = department_name.lower().replace(" ", "_")
        return self.data.DEPARTMENTS.get(key)
    
    def get_doctor_info(self, doctor_name: str) -> dict:
        """Get information about a specific doctor"""
        key = doctor_name.lower().replace(" ", "_").replace(".", "")
        return self.data.DOCTORS.get(key)
    
    def get_all_doctors(self) -> list:
        """Get list of all doctors"""
        return list(self.data.DOCTORS.values())
    
    def get_all_facilities(self) -> list:
        """Get list of all facilities"""
        return self.data.FACILITIES