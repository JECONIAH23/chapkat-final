from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import VoiceRecording, Record
import os
from .methods import transcribe_audio, call_openrouter_and_parse
import json

@csrf_exempt
def upload_voice_recording(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if 'audio_file' not in request.FILES:
        return JsonResponse({'error': 'No audio file provided'}, status=400)
        
    audio_file = request.FILES['audio_file']
    
    # Validate file size (5MB max)
    max_size = 5 * 1024 * 1024
    if audio_file.size > max_size:
        return JsonResponse({'error': 'File too large. Max 5MB allowed'}, status=400)
        
    # Validate file extension
    valid_extensions = ['.wav', '.mp3', '.ogg', '.m4a']
    ext = os.path.splitext(audio_file.name)[1].lower()
    if ext not in valid_extensions:
        return JsonResponse({
            'error': f'Unsupported file format. Supported formats: {", ".join(valid_extensions)}'
        }, status=400)
        
    try:
        recording = VoiceRecording(audio_file=audio_file)
        recording.save()
        
        # Use Sunbird for transcription
        try:
            # Convert audio file to bytes
            with open(recording.audio_file.path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
            
            # Get transcription using Sunbird
            transcription = sunbird.transcribe(audio_bytes, language='lug')
            
            # Save transcription
            voice_entry = Record.objects.create(
                original_sound=recording,
                original_text=transcription
            )
            
            # Send request to Sunbird API
            response = requests.post(
                SUNBIRD_API_URL,
                headers=SUNBIRD_HEADERS,
                json=payload
            )
            
            # Handle response
            if response.status_code == 200:
                transcription = response.json().get('transcription', '')
            else:
                raise Exception(f'Sunbird API error: {response.status_code} - {response.text}')
        except Exception as e:
            return JsonResponse({
                'error': f'Sunbird transcription failed: {str(e)}'
            }, status=500)
        
        # Use Sunbird for financial record parsing
        try:
            # Prepare request payload for financial parsing
            parsing_payload = {
                'prompt': f"""
                Parse the following Luganda voice transcription into structured financial records:
                {transcription}
                
                Return the results in JSON format with these fields:
                - date
                - amount
                - description
                - category
                """
            }
            
            # Send request to Sunbird API for parsing
            parsing_response = requests.post(
                "https://salt.sunbird.ai/api/v1/complete",
                headers=SUNBIRD_HEADERS,
                json=parsing_payload
            )
            
            # Handle parsing response
            if parsing_response.status_code == 200:
                records = parsing_response.json().get('completion', '')
            else:
                raise Exception(f'Sunbird parsing error: {parsing_response.status_code} - {parsing_response.text}')
        except Exception as e:
            return JsonResponse({
                'error': f'Sunbird parsing failed: {str(e)}'
            }, status=500)
        
        # Save the structured records
        voice_entry.processed_text = records
        voice_entry.save()
        
        return JsonResponse({
            'success': True,
            'transcription': transcription,
            'processed_records': records
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Server error while processing file',
            'details': str(e)
        }, status=500)