from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'audio', views.AudioRecordingViewSet)

urlpatterns = [
    path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('api/', include(router.urls)),
]
