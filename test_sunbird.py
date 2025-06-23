import os
import json
import requests
from urllib3 import PoolManager, disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from dotenv import load_dotenv
import base64

# Load environment variables
load_dotenv()

# Disable SSL warnings
disable_warnings(InsecureRequestWarning)

# Create HTTPS pool manager with custom SSL configuration
https = PoolManager(
    cert_reqs='CERT_NONE',  # Disable certificate verification
    assert_hostname=False
)

# Sunbird API configuration
SUNBIRD_API_URL = "https://api.sunbird.ai/tasks/stt"
AUTH_TOKEN = os.getenv('SUNBIRD_API_KEY')
HEADERS = {
    'accept': 'application/json',
    'Authorization': AUTH_TOKEN
}

def test_transcription(audio_file_path):
    try:
        # Read audio file
        with open(audio_file_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
        
        # Prepare files and data
        files = {
            'audio': (
                os.path.basename(audio_file_path),
                audio_bytes,
                'audio/mpeg'
            )
        }
        
        # Prepare form data
        data = {
            'language': 'lug',
            'adapter': 'lug',
            'whisper': True
        }
        
        # Send request to Sunbird API using HTTPS pool manager
        response = https.request(
            'POST',
            SUNBIRD_API_URL,
            headers=HEADERS,
            fields={
                'audio': (os.path.basename(audio_file_path), audio_bytes, 'audio/mpeg'),
                'language': 'lug',
                'adapter': 'lug',
                'whisper': True
            }
        )
        
        # Handle response
        if response.status_code == 200:
            transcription = response.json().get('transcription', '')
            print("\nTranscription successful!")
            print("Transcription:", transcription)
            return transcription
        else:
            print(f"\nError: {response.status_code}")
            print("Response:", response.text)
            return None
            
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def test_parsing(transcription):
    try:
        # Prepare parsing prompt
        prompt = f"""
        Parse the following Luganda voice transcription into structured financial records:
        {transcription}
        
        Return the results in JSON format with these fields:
        - date
        - amount
        - description
        - category
        """
        
        # Send parsing request using HTTPS pool manager
        parsing_response = https.request(
            'POST',
            "https://api.sunbird.ai/tasks/complete",
            headers=HEADERS,
            json={'prompt': prompt}
        )
        
        # Handle response
        if parsing_response.status_code == 200:
            records = parsing_response.json().get('completion', '')
            print("\nParsing successful!")
            print("Parsed records:", records)
            return records
        else:
            print(f"\nError in parsing: {parsing_response.status_code}")
            print("Parsing response:", parsing_response.text)
            return None
            
    except Exception as e:
        print(f"Error during parsing: {str(e)}")
        return None

if __name__ == "__main__":
    # Test with the Luganda audio file
    audio_file_path = "C:\\Users\\DIGIVERSE SOLUTIONS\\Desktop\\mm_2.mp3"
    
    # Check if file exists
    if not os.path.exists(audio_file_path):
        print(f"Error: Audio file not found at {audio_file_path}")
        exit(1)
    
    print("Testing Sunbird transcription with Luganda audio...")
    transcription = test_transcription(audio_file_path)
    
    if transcription:
        print("\nTesting financial record parsing...")
        test_parsing(transcription)
