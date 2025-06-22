from django.urls import path
from .views import UploadEpubView, HealthCheckView, TestView, TextAnalysisView, SubtitleAnalysisView

urlpatterns = [
    path('upload/', UploadEpubView.as_view(), name='upload_epub'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('test/', TestView.as_view(), name='test'),
    path('text/', TextAnalysisView.as_view(), name='analyze_text'),
    path('subtitle/', SubtitleAnalysisView.as_view(), name='analyze_subtitle'),
]
