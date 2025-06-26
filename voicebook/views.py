from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from .models import VoiceRecording, Record, AudioRecording
from .serializers import AudioRecordingSerializer
import os
import requests
from .methods import transcribe_audio, call_openrouter_and_parse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

class AudioRecordingViewSet(viewsets.ModelViewSet):
    queryset = AudioRecording.objects.all()
    serializer_class = AudioRecordingSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        # Get audio file and language from request
        audio_file = request.FILES.get('audio_file')
        language = request.data.get('language', 'lug')  # Default to Luganda if not specified
        


        if not audio_file:
            return Response({"error": "No audio file provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Get or create a default user if none exists
            from django.contrib.auth.models import User
            user = User.objects.first()
            if not user:
                user = User.objects.create_user(
                    username='default_user',
                    email='default@chapkat.com',
                    password='default_password'
                )
            
            # Read audio file
            audio_bytes = audio_file.read()
            
            # Prepare the request
            headers = {
                'accept': 'application/json',
                'Authorization': os.getenv('SUNBIRD_API_KEY')
            }
            
            # Prepare files and data
            files = {
                'audio': (
                    audio_file.name,
                    audio_bytes,
                    'audio/mp3'
                )
            }
            
            # Prepare form data
            data = {
                'language': language,
                'adapter': language,
                'whisper': True
            }
            
            # Make the API request
            response = requests.post(
                "https://api.sunbird.ai/tasks/stt",
                headers=headers,
                files=files,
                data=data
            )
            
            # Check for successful response
            if response.status_code == 200:
                transcription = response.json().get('transcription', '')
                
                # Save the audio recording with transcription
                recording = AudioRecording.objects.create(
                    user=user,
                    audio_file=audio_file,
                    transcription=transcription
                )
                
                # Return response with transcription
                return Response({
                    'success': True,
                    'transcription': transcription,
                    'language': language
                }, status=status.HTTP_201_CREATED)
            else:
                raise Exception(f"Sunbird API error: {response.status_code} - {response.text}")
            
            # Save the audio recording with transcription
            recording = AudioRecording.objects.create(
                audio_file=audio_file,
                transcription=transcription
            )
            
            # Return response with transcription
            return Response({
                'success': True,
                'transcription': transcription,
                'language': language
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Failed to process audio: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)