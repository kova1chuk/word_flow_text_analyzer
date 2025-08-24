from django.urls import path
from .views import EpubAnalysisView, HealthCheckView, TestView, TextAnalysisView, SubtitleAnalysisView
from .views.image import ImageAnalysisView, ImageAnalysisHealthView
from .views.batch_image import BatchImageAnalysisView, BatchImageAnalysisStatusView, BatchImageAnalysisResultsView

urlpatterns = [
    path('epub', EpubAnalysisView.as_view(), name='upload_epub'),
    path('health', HealthCheckView.as_view(), name='health_check'),
    path('test', TestView.as_view(), name='test'),
    path('text', TextAnalysisView.as_view(), name='analyze_text'),
    path('subtitle', SubtitleAnalysisView.as_view(), name='analyze_subtitle'),
    path('image', ImageAnalysisView.as_view(), name='analyze_image'),
    path('image/health', ImageAnalysisHealthView.as_view(),
         name='image_health_check'),
    # Temporarily disabled to fix Swagger issues
    # path('image/batch', BatchImageAnalysisView.as_view(),
    #      name='batch_analyze_images'),
    # path('image/batch/status',
    #      name='batch_status'),
    # path('image/batch/results',
    #      name='batch_results'),
]
