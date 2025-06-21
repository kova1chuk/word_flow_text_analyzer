from django.urls import path
from .views import UploadEpubView

urlpatterns = [
    path('upload/', UploadEpubView.as_view(), name='upload_epub'),
]
