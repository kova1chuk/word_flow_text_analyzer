from django.urls import path
from .views import UploadEpubView, HealthCheckView

urlpatterns = [
    path('upload/', UploadEpubView.as_view(), name='upload_epub'),
    path('health/', HealthCheckView.as_view(), name='health_check'),
]
