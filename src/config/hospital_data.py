"""
Hospital Data Configuration
==========================
Edit this file to customize all hospital information.
This data is accessed via tools/functions to save tokens.
"""

HOSPITAL_INFO = {
    "name": "Delhi Hospital",
    "type": "NABH Accredited Multispecialty Hospital",
    "tagline": "Aapki sehat, hamari zimmedari",
    
    "address": "Sampla Road, Near Prince Hotel, Kharkhoda, Sonipat, Haryana 131402",
    "landmark": "Near Prince Hotel, on Sampla/Kharkhoda Main Road",
    
    "phones": {
        "primary": "+91 99849 41611",
        "secondary": "+91 97290 17553",
        "alternate": "+91 98133 79592"
    },
    "email": "delhihospitalkkd@gmail.com",
    "website": "delhihospital.co.in",
    
    "hours": {
        "hospital": "24x7 (Open all days)",
        "emergency": "24x7",
        "icu": "24x7",
        "opd": "Daytime hours - confirm with reception for specific doctor",
        "pharmacy": "24x7",
        "lab": "7:00 AM - 9:00 PM"
    },
    
    "accreditation": ["NABH Accredited", "CGHS Delhi/NCR Empanelled"],
    
    "facilities": [
        "24x7 Emergency & Trauma Services",
        "Fully Equipped ICU & Critical Care",
        "Advanced Pathology Lab",
        "Digital X-ray & Ultrasound",
        "Modern Operation Theatres",
        "In-house Pharmacy",
        "Private & Semi-private Rooms",
        "24x7 Ambulance Service"
    ]
}

# Doctors organized by department
DOCTORS = {
    "orthopedics": {
        "department_name": "Orthopedics & Joint Replacement",
        "handles": ["fractures", "joint pain", "arthritis", "ligament injuries", "knee pain", "hip pain", "back pain", "spine issues", "sports injury"],
        "doctors": [
            {
                "name": "Dr. Anil Sharma",
                "designation": "Joint Replacement & Orthopaedics Specialist",
                "specialization": "Joint Replacement, Fractures, Arthritis, Sports Injuries",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "ent": {
        "department_name": "ENT (Ear, Nose, Throat)",
        "handles": ["ear pain", "ear discharge", "hearing loss", "sinus", "sore throat", "tonsils", "vertigo", "nose block"],
        "doctors": [
            {
                "name": "Dr. Ravi Shankar",
                "designation": "ENT Specialist",
                "specialization": "Ear, Nose, Throat disorders, Sinus, Vertigo",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "eye": {
        "department_name": "Ophthalmology (Eye)",
        "handles": ["eye redness", "eye pain", "blurred vision", "itching", "eye infection", "vision checkup"],
        "doctors": [
            {
                "name": "Dr. Divya Dhingra",
                "designation": "Eye Specialist",
                "specialization": "Eye Care, Vision Problems, Eye Infections",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "gynecology": {
        "department_name": "Gynaecology & Obstetrics",
        "handles": ["pregnancy", "periods problem", "menstrual issues", "white discharge", "PCOS", "fertility", "women health"],
        "doctors": [
            {
                "name": "Dr. Mamta Sharma",
                "designation": "Gynaecologist",
                "specialization": "Pregnancy Care, Menstrual Problems, PCOS, Women's Health",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "pediatrics": {
        "department_name": "Pediatrics (Child Care)",
        "handles": ["child fever", "baby health", "vaccination", "child cough", "growth issues", "newborn care"],
        "doctors": [
            {
                "name": "Dr. S Kumar",
                "designation": "Paediatrician",
                "specialization": "Child Health, Vaccinations, Growth & Development",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "urology": {
        "department_name": "Urology",
        "handles": ["kidney stone", "burning urination", "urine problem", "prostate", "blood in urine"],
        "doctors": [
            {
                "name": "Dr. Anil Aggarwal",
                "designation": "Urologist",
                "specialization": "Kidney Stones, Urinary Problems, Prostate Issues",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "plastic_surgery": {
        "department_name": "Plastic, Cosmetic & Burn Surgery",
        "handles": ["burns", "scars", "cosmetic surgery", "reconstructive surgery"],
        "doctors": [
            {
                "name": "Dr. Tapeshwar Shegal",
                "designation": "Burn, Cosmetic & Plastic Surgeon",
                "specialization": "Burns, Scar Revision, Cosmetic & Reconstructive Surgery",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "general_surgery": {
        "department_name": "General & Laparoscopic Surgery",
        "handles": ["hernia", "gallbladder", "appendix", "piles", "fissure", "surgery"],
        "doctors": [
            {
                "name": "Dr. Shushant Verma",
                "designation": "General & Laparoscopic Surgeon",
                "specialization": "Hernia, Gallbladder, Appendix, Piles, Laparoscopic Surgery",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "physiotherapy": {
        "department_name": "Physiotherapy & Rehabilitation",
        "handles": ["physio", "rehab", "exercise", "stiffness", "post surgery rehab", "stroke rehab"],
        "doctors": [
            {
                "name": "Dr. Vinay Chand",
                "designation": "Physiotherapist",
                "specialization": "Post-surgery Rehab, Joint Stiffness, Sports Rehab",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "radiology": {
        "department_name": "Radiology & Imaging",
        "handles": ["xray", "ultrasound", "imaging", "scan"],
        "doctors": [
            {
                "name": "Dr. Ruchi Sharma",
                "designation": "Radiologist",
                "specialization": "X-ray, Ultrasound, Diagnostic Imaging",
                "timings": "Please confirm with reception",
                "consultation_fee": "On prescription from doctor"
            }
        ]
    },
    
    "diet": {
        "department_name": "Diet & Nutrition",
        "handles": ["diet", "weight", "nutrition", "diabetes diet", "heart diet"],
        "doctors": [
            {
                "name": "Vanshika Dahiya",
                "designation": "Dietician",
                "specialization": "Weight Management, Diabetes Diet, Heart-healthy Diet",
                "timings": "Please confirm with reception",
                "consultation_fee": "Confirm with reception"
            }
        ]
    },
    
    "anaesthesia": {
        "department_name": "Anaesthesia (Internal)",
        "handles": [],  # Not for direct booking
        "doctors": [
            {
                "name": "Dr. Amit Sahu",
                "designation": "Anaesthetist",
                "specialization": "Surgery Support, ICU, Procedures",
                "timings": "Part of surgical/ICU team",
                "consultation_fee": "N/A - Internal use only"
            }
        ]
    }
}

# Emergency symptoms - immediate ER referral
EMERGENCY_SYMPTOMS = [
    "severe chest pain",
    "difficulty breathing", 
    "breathlessness with sweating",
    "stroke symptoms",
    "sudden weakness one side",
    "slurred speech",
    "uncontrolled bleeding",
    "major injury",
    "loss of consciousness",
    "severe burns",
    "chemical in eye",
    "sudden vision loss",
    "pregnant with bleeding",
    "severe abdominal pain with vomiting",
    "high fever with confusion",
    "seizure",
    "poisoning"
]

# ============================================
# FREE SECOND OPINION SERVICE
# ============================================
SECOND_OPINION_SERVICE = {
    "name": "Free Second Opinion Service",
    "website": "secondopinion.org",
    "cost": "Completely FREE (online + offline appointment)",
    "hospital": "Delhi Hospital, Kharkhoda",
    
    "description": """
Delhi Hospital offers a FREE Second Opinion Service. Start online by uploading 
your reports, and get a FREE in-person appointment at the hospital. Senior 
specialists review your case and guide you on whether surgery or treatment is 
actually needed. No charges at any step.
""".strip(),
    
    "how_it_works": [
        "1. Visit secondopinion.org or WhatsApp your reports to +91 99849 41611",
        "2. Upload your medical reports (X-ray, MRI, prescriptions, etc.)",
        "3. Senior doctors review your case within 24-48 hours",
        "4. You get a FREE offline appointment at Delhi Hospital",
        "5. Meet the specialist in-person for final consultation - absolutely free"
    ],
    
    "benefits": [
        "100% FREE - Online review + Offline appointment, no hidden costs",
        "Start from home - just upload reports online",
        "Expert review by senior specialists",
        "Get FREE in-person consultation at hospital",
        "Avoid unnecessary surgeries - get honest opinion",
        "No obligation - decide after meeting the doctor"
    ],
    
    "who_should_use": [
        "Patients advised for surgery who want confirmation",
        "People with joint, spine, or arthritis issues",
        "Cases with confusing or conflicting reports",
        "Anyone wanting expert opinion before starting treatment"
    ],
    
    "documents_needed": {
        "recommended": ["X-ray", "MRI", "CT Scan", "Blood reports", "Previous prescriptions", "Surgery recommendation notes"],
        "note": "Documents help but are optional - you can discuss even without reports"
    },
    
    "specialties_covered": [
        "Orthopedics & Joint Replacement",
        "Spine Issues",
        "Arthritis",
        "Sports Injuries",
        "General Surgery cases"
    ],
    
    "contact": {
        "website": "secondopinion.org",
        "whatsapp": "+91 99849 41611",
        "phone": "+91 99849 41611"
    }
}


# ============================================
# HELPER FUNCTIONS (called by tools)
# ============================================

def get_all_doctors_summary() -> str:
    """Get a brief list of all doctors"""
    result = []
    for dept_key, dept in DOCTORS.items():
        if dept["doctors"] and dept["handles"]:  # Skip internal departments
            for doc in dept["doctors"]:
                result.append(f"• {doc['name']} - {dept['department_name']}")
    return "\n".join(result)


def get_doctor_details(doctor_name: str) -> str:
    """Get detailed info about a specific doctor"""
    doctor_name_lower = doctor_name.lower()
    for dept_key, dept in DOCTORS.items():
        for doc in dept["doctors"]:
            if doctor_name_lower in doc["name"].lower():
                return f"""
Doctor: {doc['name']}
Department: {dept['department_name']}
Designation: {doc['designation']}
Specialization: {doc['specialization']}
Timings: {doc['timings']}
Fee: {doc['consultation_fee']}
"""
    return "Doctor not found. Please check the name or ask reception."


def get_department_info(department: str) -> str:
    """Get info about a department"""
    dept_lower = department.lower()
    for dept_key, dept in DOCTORS.items():
        if dept_lower in dept_key or dept_lower in dept["department_name"].lower():
            doctors_list = "\n".join([f"  • {d['name']} - {d['designation']}" for d in dept["doctors"]])
            conditions = ", ".join(dept["handles"]) if dept["handles"] else "N/A"
            return f"""
Department: {dept['department_name']}
Conditions Treated: {conditions}
Doctors:
{doctors_list}
"""
    return "Department not found."


def get_hospital_info() -> str:
    """Get hospital contact and timing info"""
    h = HOSPITAL_INFO
    return f"""
Hospital: {h['name']}
Address: {h['address']}
Landmark: {h['landmark']}
Phone: {h['phones']['primary']}
Alt Phones: {h['phones']['secondary']}, {h['phones']['alternate']}
Email: {h['email']}
Website: {h['website']}
Emergency: {h['hours']['emergency']}
OPD: {h['hours']['opd']}
"""


def get_facilities() -> str:
    """Get hospital facilities list"""
    return "Hospital Facilities:\n" + "\n".join([f"- {f}" for f in HOSPITAL_INFO["facilities"]])


def get_second_opinion_info() -> str:
    """Get information about the free second opinion service"""
    s = SECOND_OPINION_SERVICE
    
    how_it_works = "\n".join(s["how_it_works"])
    benefits = "\n".join([f"- {b}" for b in s["benefits"]])
    who_should_use = "\n".join([f"- {w}" for w in s["who_should_use"]])
    docs = ", ".join(s["documents_needed"]["recommended"])
    
    return f"""
{s['name']}
Website: {s['website']}
Cost: {s['cost']}

{s['description']}

HOW IT WORKS:
{how_it_works}

BENEFITS:
{benefits}

WHO SHOULD USE:
{who_should_use}

DOCUMENTS (optional, but recommended):
{docs}
Note: {s['documents_needed']['note']}

CONTACT:
WhatsApp/Phone: {s['contact']['phone']}
Website: {s['contact']['website']}
"""


def get_all_specialties_for_routing() -> str:
    """
    Returns ALL departments with what they handle.
    AI uses this to intelligently recommend the best specialty.
    """
    # Check emergencies first
    emergency_list = ", ".join(EMERGENCY_SYMPTOMS[:8]) + "..."
    
    result = f"""HOSPITAL SPECIALTIES - Use this to recommend the right doctor

EMERGENCIES (send to ER immediately): {emergency_list}
ER Phone: +91 99849 41611

DEPARTMENTS:\n"""
    
    for dept_key, dept_info in DOCTORS.items():
        if not dept_info.get("handles"):  # Skip internal depts like anaesthesia
            continue
            
        name = dept_info["department_name"]
        handles = ", ".join(dept_info["handles"])
        doctor = dept_info["doctors"][0]["name"] if dept_info["doctors"] else "Specialist"
        
        result += f"\n- {name}\n  Handles: {handles}\n  Doctor: {doctor}\n"
    
    result += """
SECOND OPINION SERVICE (secondopinion.org):
If patient mentions surgery/operation was advised by another doctor, suggest our FREE Second Opinion service. They can upload reports online for specialist review.

Reception for appointments: +91 99849 41611
"""
    return result
