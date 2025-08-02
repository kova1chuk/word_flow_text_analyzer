from django.urls import path
from .views import EpubAnalysisView, HealthCheckView, TestView, TextAnalysisView, SubtitleAnalysisView

urlpatterns = [
    path('epub/', EpubAnalysisView.as_view(), name='upload_epub'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('test/', TestView.as_view(), name='test'),
    path('text/', TextAnalysisView.as_view(), name='analyze_text'),
    path('subtitle/', SubtitleAnalysisView.as_view(), name='analyze_subtitle'),
]
