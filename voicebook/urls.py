from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_voice_recording, name='upload_voice_recording'),
]
