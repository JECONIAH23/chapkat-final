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
        
        # Mock transcription for testing
        
        transcription = transcribe_audio(recording.audio_file.path)
        if transcription.get("error"):
            transcription = "Natunze amenvu ataano"
        
        # Save transcription
        voice_entry = Record.objects.create(original_sound=recording, original_text=transcription)
        
        # Call OpenRouter for financial record parsing
        records = call_openrouter_and_parse(request.user, transcription, voice_entry)
        
        # Prepare structured output
        return JsonResponse({
            "original_transcription": transcription,
            "financial_records": [{
                "product_name": r.product_name,
                "quantity": r.quantity,
                "unit_price": float(r.unit_price),
                "total_price": float(r.total_price),
                "transaction_type": r.transaction_type
            } for r in records]
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Server error while processing file',
            'details': str(e)
        }, status=500)