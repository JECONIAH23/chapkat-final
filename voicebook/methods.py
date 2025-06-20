import requests
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables (optional)
load_dotenv()

# Sunbird AI API configuration
SUNBIRD_API_KEY = os.getenv('SUNBIRD_API_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiZW5nYW5ha2lsbGlhbiIsImFjY291bnRfdHlwZSI6IkZyZWUiLCJleHAiOjQ5MDE0NDAwNDl9.iXft_dGDVWN8b6hESmKx_YVcifW8-v64esY1j8zUAs0')
SUNBIRD_API_URL = "https://api.sunbird.ai/v1/audio/transcribe"  # Check for the correct endpoint

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

