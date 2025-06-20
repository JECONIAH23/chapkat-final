import requests
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables (optional)
load_dotenv()

# Sunbird AI API configuration
SUNBIRD_API_KEY = os.getenv('SUNBIRD_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZW5nYW5ha2lsbGlhbiIsImFjY291bnRfdHlwZSI6IkZyZWUiLCJleHAiOjQ5MDE0NDAwNDl9.iXft_dGDVWN8b6hESmKx_YVcifW8-v64esY1j8zUAs0')
# SUNBIRD_API_URL = "https://api.sunbird.ai/v1/audio/transcribe"  # Check for the correct endpoint
SUNBIRD_API_URL = "https://api.sunbird.ai/tasks/nllb_translate"  # Check for the correct endpoint

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using Sunbird AI API
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        
    Returns:
        dict: API response containing transcription
    """
    try:
        # Prepare the request
        headers = {
            "Authorization": f"Bearer {SUNBIRD_API_KEY}",
        }
        
        # Check if file exists
        if not Path(audio_file_path).is_file():
            return {"error": "Audio file not found"}
        
        # Read audio file
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                'audio': (os.path.basename(audio_file_path), audio_file)
            }
            
            # Make the API request
            response = requests.post(
                SUNBIRD_API_URL,
                headers=headers,
                files=files
            )
            
            # Check for successful response
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": "API request failed",
                    "status_code": response.status_code,
                    "response": response.text
                }
                
    except Exception as e:
        return {"error": str(e)}


def call_openrouter_and_parse(user, text, source_entry=None):
    """
    Parse financial records from text using OpenRouter API
    
    Args:
        user: Django User object
        text: Text to parse
        source_entry: Optional source entry for reference
        
    Returns:
        list: List of parsed financial records
    """
    prompt = f"""
You are a financial assistant. A user has just recorded this transaction using voice:
"{text}"

Please extract structured financial records from it in the following JSON format:
[
  {{
    "product_name": "string",
    "quantity": integer,
    "unit_price": float,
    "transaction_type": "Sold" or "Bought"
  }}
]

Only return valid JSON. Do not add any text or explanation.
"""

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "SME-Voice-App"
    }

    payload = {
        "model": "mistralai/devstral-small:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = response.json()
        reply = data["choices"][0]["message"]["content"]

        # Clean markdown-style code block
        reply = reply.strip()
        if reply.startswith("```json"):
            reply = reply.replace("```json", "").strip()
        if reply.endswith("```"):
            reply = reply[:-3].strip()

        records = json.loads(reply)

        saved = []
        for rec in records:
            saved.append(FinancialRecord.objects.create(
                user=user,
                product_name=rec["product_name"],
                quantity=rec["quantity"],
                unit_price=rec["unit_price"],
                total_price=rec["quantity"] * rec["unit_price"],
                source_text=source_entry
            ))
        return saved

    except Exception as e:
        print("LLM error:", e)
        return []

