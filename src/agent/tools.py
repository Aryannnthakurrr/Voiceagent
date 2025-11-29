"""
Tools for OpenAI Realtime API Function Calling
===============================================
These tools let the model fetch hospital data on-demand instead of
having everything in the system prompt (saves tokens = saves cost!)
"""

from config.hospital_data import (
    get_all_doctors_summary,
    get_doctor_details,
    get_department_info,
    get_hospital_info,
    get_facilities,
    get_all_specialties_for_routing,
    get_second_opinion_info,
    HOSPITAL_INFO,
    DOCTORS
)

# Tool definitions for OpenAI Realtime API
TOOLS = [
    {
        "type": "function",
        "name": "get_hospital_info",
        "description": "Get hospital contact details including address, phone numbers, email, website, and operating hours. Use this when caller asks about hospital location, contact, or timings.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_facilities",
        "description": "Get list of hospital facilities and services like ICU, lab, pharmacy, ambulance, operation theatres. Use when caller asks what services are available.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_all_doctors",
        "description": "Get a summary list of all doctors with their departments. Use when caller asks to know available doctors or wants an overview.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_doctor_details",
        "description": "Get detailed information about a specific doctor including specialization, department, and timing. Use when caller asks about a specific doctor by name.",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {
                    "type": "string",
                    "description": "Name or partial name of the doctor to look up"
                }
            },
            "required": ["doctor_name"]
        }
    },
    {
        "type": "function",
        "name": "get_department_info",
        "description": "Get information about a specific department including doctors and conditions treated. Use when caller asks about a specialty like orthopedics, gynecology, etc.",
        "parameters": {
            "type": "object",
            "properties": {
                "department": {
                    "type": "string",
                    "description": "Department name like 'orthopedics', 'ent', 'eye', 'gynecology', 'pediatrics', 'urology', etc."
                }
            },
            "required": ["department"]
        }
    },
    {
        "type": "function",
        "name": "get_specialties",
        "description": "Get ALL hospital departments with what conditions each handles. Use this to intelligently recommend the best specialty for a patient's symptoms. YOU decide which department fits best based on their symptoms.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "type": "function",
        "name": "get_second_opinion_info",
        "description": "Get details about the hospital's FREE online second opinion service at secondopinion.org. Use when caller asks about second opinion, wants to verify if surgery is needed, mentions being confused about diagnosis, or wants expert review of their case before deciding on treatment.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> str:
    """
    Execute a tool call and return the result.
    
    Args:
        tool_name: Name of the tool to call
        arguments: Dictionary of arguments for the tool
    
    Returns:
        String result to be sent back to the model
    """
    try:
        if tool_name == "get_hospital_info":
            return get_hospital_info()
        
        elif tool_name == "get_facilities":
            return get_facilities()
        
        elif tool_name == "get_all_doctors":
            return get_all_doctors_summary()
        
        elif tool_name == "get_doctor_details":
            doctor_name = arguments.get("doctor_name", "")
            return get_doctor_details(doctor_name)
        
        elif tool_name == "get_department_info":
            department = arguments.get("department", "")
            return get_department_info(department)
        
        elif tool_name == "get_specialties":
            return get_all_specialties_for_routing()
        
        elif tool_name == "get_second_opinion_info":
            return get_second_opinion_info()
        
        else:
            return f"Unknown tool: {tool_name}"
    
    except Exception as e:
        return f"Error executing tool: {str(e)}"


# Export for voice_agent.py
__all__ = ['TOOLS', 'handle_tool_call']
