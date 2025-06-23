import os
import http.client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
SUNBIRD_API_URL = "api.sunbird.ai"
AUTH_TOKEN = os.getenv('SUNBIRD_API_KEY')
HEADERS = {
    'accept': 'application/json',
    'Authorization': AUTH_TOKEN
}

def test_api():
    try:
        # Test root endpoint with curl
        print("Testing API connection with curl...")
        curl_cmd = [
            'curl',
            '-k',  # Disable SSL verification
            '-H', f'Authorization: {AUTH_TOKEN}',
            '-H', 'accept: application/json',
            'https://api.sunbird.ai/'
        ]
        
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        print(f"\nRoot endpoint status: {result.returncode}")
        print("Response:", result.stdout)
        
        # Test STT endpoint with curl
        print("\nTesting STT endpoint with curl...")
        stt_cmd = [
            'curl',
            '-k',  # Disable SSL verification
            '-X', 'POST',
            '-H', f'Authorization: {AUTH_TOKEN}',
            '-H', 'accept: application/json',
            '-F', 'language=lug',
            '-F', 'adapter=lug',
            '-F', 'whisper=true',
            SUNBIRD_API_URL
        ]
        
        stt_result = subprocess.run(stt_cmd, capture_output=True, text=True)
        print(f"\nSTT endpoint status: {stt_result.returncode}")
        print("Response:", stt_result.stdout)
        
    except Exception as e:
        print(f"Error testing API: {str(e)}")

if __name__ == "__main__":
    test_api()
