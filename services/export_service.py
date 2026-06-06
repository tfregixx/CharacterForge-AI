import json
from fpdf import FPDF
from datetime import datetime

def export_to_json(character_data):
    """
    Export character to JSON format.
    
    Args:
        character_data: Dictionary with character info
    
    Returns:
        JSON string
    """
    export_data = {
        "name": character_data.get("name", ""),
        "genre": character_data.get("genre", ""),
        "content": character_data.get("content", ""),
        "exported_at": datetime.utcnow().isoformat(),
        "exported_from": "CharacterForge AI"
    }
    
    return json.dumps(export_data, indent=2)

def export_to_txt(character_data):
    """
    Export character to TXT format.
    
    Args:
        character_data: Dictionary with character info
    
    Returns:
        Text string
    """
    text = f"""
CHARACTER CARD
{'='*50}

Name: {character_data.get('name', 'N/A')}
Genre: {character_data.get('genre', 'N/A')}
Created: {character_data.get('created_at', 'N/A')}

{'='*50}
CHARACTER DETAILS:
{'='*50}

{character_data.get('content', '')}

{'='*50}
Exported from CharacterForge AI
Export Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}
"""
    return text

def export_to_pdf(character_data):
    """
    Export character to PDF format.
    
    Args:
        character_data: Dictionary with character info
    
    Returns:
        Bytes of PDF file
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "CHARACTER CARD", ln=True, align="C")
        
        # Header info
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 10, f"Name: {character_data.get('name', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Genre: {character_data.get('genre', 'N/A')}", ln=True)
        pdf.cell(0, 10, f"Created: {character_data.get('created_at', 'N/A')}", ln=True)
        
        # Divider
        pdf.ln(5)
        pdf.set_draw_color(0, 0, 0)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        
        # Character details
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "CHARACTER DETAILS:", ln=True)
        
        pdf.set_font("Arial", "", 10)
        
        # Wrap text for content
        content = character_data.get('content', '')
        pdf.multi_cell(0, 5, content)
        
        # Footer
        pdf.ln(5)
        pdf.set_font("Arial", "I", 9)
        pdf.cell(0, 10, f"Exported from CharacterForge AI on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}", align="C")
        
        return pdf.output()
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

def save_export(character_name, format_type, data):
    """
    Save exported character to file.
    
    Args:
        character_name: Name of the character
        format_type: Format (json, txt, pdf)
        data: The exported data
    
    Returns:
        Path to saved file or None
    """
    import os
    
    os.makedirs("exports", exist_ok=True)
    
    try:
        if format_type == "json":
            filename = f"exports/{character_name.replace(' ', '_')}.json"
            with open(filename, 'w') as f:
                f.write(data)
        
        elif format_type == "txt":
            filename = f"exports/{character_name.replace(' ', '_')}.txt"
            with open(filename, 'w') as f:
                f.write(data)
        
        elif format_type == "pdf":
            filename = f"exports/{character_name.replace(' ', '_')}.pdf"
            with open(filename, 'wb') as f:
                f.write(data)
        
        else:
            return None
        
        return filename
    except Exception as e:
        print(f"Error saving export: {e}")
        return None
