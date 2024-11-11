from pipeline import Document

# Create example document template based on summary type
EXAMPLE_TEMPLATES = {
    "detailed": Document({
        "Water": """Comprehensive analysis of water-related issues including detailed flood data, 
        port operations metrics, and infrastructure status...""",
        "Fire": """Detailed fire services report including station locations, response times, 
        equipment inventory, and wildfire incident analysis...""",
        "Administrative": """Complete administrative overview including staff counts, facility status, 
        training metrics, and operational protocols...""",
        "Other": """Detailed miscellaneous information including all auxiliary systems, 
        community programs, and external partnerships..."""
    }),
    "brief": Document({
        "Water": """Key water-related highlights and critical flood/port updates.""",
        "Fire": """Essential fire service updates and major incident summary.""",
        "Administrative": """Core administrative metrics and key operational changes.""",
        "Other": """Brief overview of other significant developments."""
    })
}