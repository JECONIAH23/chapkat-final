from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import VoiceRecording
import os
from .methods import transcribe_audio

@csrf_exempt
def upload_voice_recording(request):
    if request.method == 'POST':
        try:
            audio_file = request.FILES.get('audio_file')
            if not audio_file:
                return JsonResponse({'error': 'No audio file provided'}, status=400)
                
            recording = VoiceRecording(audio_file=audio_file)
            recording.save()
            

            # Process the audio file
        
            # audio_file = "path/to/your/audio/file.wav"  # Replace with your audio file path
            audio_file = recording.audio_file.url
            result = transcribe_audio(audio_file)
            if 'text' in result:
                print("\nTranscribed Text:")
                print(result['text'])


















            

            return JsonResponse({
                'message': 'Voice recording uploaded successfully',
                'id': recording.id,
                'file_path': recording.audio_file.url
            }, status=201)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)
