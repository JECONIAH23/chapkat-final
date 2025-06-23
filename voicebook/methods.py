import requests
from dotenv import load_dotenv
import os
from pathlib import Path
import json


# Load environment variables (optional)
load_dotenv()

# Sunbird AI API configuration
SUNBIRD_API_KEY = os.getenv('SUNBIRD_API_KEY')
if not SUNBIRD_API_KEY:
    raise ValueError("SUNBIRD_API_KEY environment variable is not set")

# API Endpoints
SUNBIRD_STT_URL = "https://api.sunbird.ai/v1/stt"
SUNBIRD_TRANSLATE_URL = "https://api.sunbird.ai/v1/translate"

# def transcribe_audio(audio_file_path):
#     """
#     Transcribe audio file using Sunbird AI API
    
#     Args:
#         audio_file_path (str): Path to the audio file to transcribe
        
#     Returns:
#         dict: API response containing transcription
#     """
#     try:
#         # Prepare the request
#         headers = {
#             "Authorization": f"Bearer {SUNBIRD_API_KEY}",
#         }
        
#         # Check if file exists
#         if not Path(audio_file_path).is_file():
#             return {"error": "Audio file not found"}
        
#         # Read audio file
#         with open(audio_file_path, 'rb') as audio_file:
#             files = {
#                 'audio': (os.path.basename(audio_file_path), audio_file)
#             }
            
#             # Make the API request
#             response = requests.post(
#                 SUNBIRD_API_URL,
#                 headers=headers,
#                 files=files
#             )
            
#             # Check for successful response
#             if response.status_code == 200:
#                 return response.json()
#             else:
#                 return {
#                     "error": "API request failed",
#                     "status_code": response.status_code,
#                     "response": response.text
#                 }
                
#     except Exception as e:
#         return {"error": str(e)}


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


def transcribe_audio(audio_file_path, language="lug"):
    """
    Process audio file through STT and translation pipeline
    
    Args:
        audio_file_path (str): Path to the audio file
        language (str): Source language code (default: "lug" for Luganda)
        
    Returns:
        dict: {
            "transcription": str, 
            "translation": str,
            "error": str (if any)
        }
    """
    try:
        # 1. Validate file exists
        if not Path(audio_file_path).is_file():
            return {"error": "Audio file not found"}

        # 2. Speech-to-Text (STT) API Call
        stt_url = SUNBIRD_STT_URL
        stt_headers = {
            "Authorization": f"Bearer {SUNBIRD_API_KEY}"
        }

        # Prepare the request payload
        payload = {
            "language": language,
            "model": "whisper"
        }
        
        with open(audio_file_path, 'rb') as audio_file:
            files = {
                "audio_file": (os.path.basename(audio_file_path), audio_file, 'audio/mpeg')
            }
            
            stt_response = requests.post(
                stt_url, 
                headers=stt_headers,
                data=payload,
                files=files
            )
            stt_response.raise_for_status()
            transcription = stt_response.json().get("audio_transcription", "")

        # 3. Translation API Call (Sunbird)
        if transcription:
            translation_url = "https://api.sunbird.ai/tasks/nllb_translate"
            translation_headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {os.getenv('SUNBIRD_API_KEY')}",
                "Content-Type": "application/json",
            }

            translation_payload = {
                "source": language,
                "target": "eng",
                "text": transcription
            }

            translation_response = requests.post(
                translation_url, 
                headers=translation_headers, 
                json=translation_payload
            )
            translation_response.raise_for_status()
            translated_text = translation_response.json().get("output", {}).get("translated_text", "")

            return {
                "transcription": transcription,
                "translation": translated_text
            }
        
        return {"error": "No transcription generated"}

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Processing failed: {str(e)}"}


# def call_openrouter_and_parse(user, text, source_entry=None):
#     """Parse financial records from text using LLM"""
#     prompt = f"""Extract financial transactions from: "{text}"
#     Return JSON format: [{"product_name":str, "quantity":int, "unit_price":float, "transaction_type":str}]"""
    
#     headers = {
#         "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
#         "Content-Type": "application/json"
#     }
    
#     payload = {
#         "model": "mistralai/mistral-7b-instruct",
#         "messages": [{"role": "user", "content": prompt}]
#     }

#     try:
#         response = requests.post(
#             "https://openrouter.ai/api/v1/chat/completions",
#             headers=headers,
#             json=payload
#         )
#         response.raise_for_status()
#         content = response.json()["choices"][0]["message"]["content"]
        
#         # Clean JSON response
#         if content.startswith("```json"):
#             content = content[7:-3].strip()
        
#         records = json.loads(content)
        
#         # Create and return Record objects
#         return [
#             Record.objects.create(
#                 user=user,
#                 product_name=r["product_name"],
#                 quantity=r.get("quantity", 1),
#                 unit_price=r["unit_price"],
#                 total_price=r.get("total_price", r["unit_price"] * r.get("quantity", 1)),
#                 transaction_type=r.get("transaction_type", "sale").upper(),
#                 original_text=source_entry
#             ) for r in records
#         ]
        
#     except Exception as e:
#         print(f"LLM parsing error: {str(e)}")
#         return []