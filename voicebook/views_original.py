from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import VoiceRecording, Record
import os
from .methods import transcribe_audio, call_openrouter_and_parse
from rest_framework.response import Response
from rest_framework import status

# @csrf_exempt
# def upload_voice_recording(request):
#     if request.method == 'POST':
#         try:
#             audio_file = request.FILES.get('audio_file')
#             if not audio_file:
#                 return JsonResponse({'error': 'No audio file provided'}, status=400)
                
#             recording = VoiceRecording(audio_file=audio_file)
#             recording.save()
            

#             # Process the audio file
        
#             # audio_file = "path/to/your/audio/file.wav"  # Replace with your audio file path
#             


#             # Get the relative path of the uploaded file
#             file_path = recording.audio_file.name
            
#             return JsonResponse({
#                 'message': 'Voice recording uploaded successfully',
#                 'id': recording.id,
#                 'file_path': file_path,
#                 'created_at': recording.created_at.isoformat()
#             }, status=201)
            
#         except Exception as e:
#             return JsonResponse({'error': str(e)}, status=500)
            
#     return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def upload_voice_recording(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
        
    if not request.FILES:
        return JsonResponse({'error': 'No files uploaded'}, status=400)
        
    if 'audio_file' not in request.FILES:
        return JsonResponse({'error': 'Key "audio_file" not found in uploaded files'}, status=400)
        
    audio_file = request.FILES['audio_file']
    
    # Validate file size (e.g., 5MB max)
    max_size = 5 * 1024 * 1024  # 5MB
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
        
        # Here you would typically call your transcribe_audio function
        # audio_file = recording.audio_file.url
        # result = transcribe_audio(audio_file)
        # transcription = transcribe_audio(recording.audio_file.path)
        transcription = "Natunze amenvu ataano"


        ################ MODEL INTERPRETATION ################

        # Save transcription
        voice_entry = Record.objects.create(original_sound=recording, original_text=transcription)

        # Call OpenRouter for financial record parsing
        records = call_openrouter_and_parse(None, transcription, voice_entry)

        # Prepare structured output
        return Response({
            "original_transcription": transcription,
            "financial_records": [{
                "product_name": r.product_name,
                "quantity": r.quantity,
                "unit_price": float(r.unit_price),
                "total_price": float(r.total_price),
                "transaction_type": r.transaction_type
            } for r in records]
        }, status=status.HTTP_201_CREATED)



        ################ MODEL INTERPRETATION END ################

        return JsonResponse({
            'success': True,
            'id': recording.id,
            'file_url': recording.audio_file.url,
            'message': transcription
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Server error while processing file',
            'details': str(e)
        }, status=500)