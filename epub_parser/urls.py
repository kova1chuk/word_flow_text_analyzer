from django.urls import path
from .views import UploadEpubView, HealthCheckView, TestView

urlpatterns = [
    path('upload/', UploadEpubView.as_view(), name='upload_epub'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('test/', TestView.as_view(), name='test'),
]
