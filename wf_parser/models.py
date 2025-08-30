from django.db import models
from django.utils import timezone
import json


class ImageAnalysisResult(models.Model):
    """Model to store image analysis results"""

    # Basic information
    image_name = models.CharField(max_length=255)
    image_size = models.BigIntegerField(help_text="Image size in bytes")
    content_type = models.CharField(max_length=100)

    # OCR results
    extracted_text = models.TextField()
    detected_language = models.CharField(max_length=10)
    confidence_score = models.FloatField()
    ocr_engine = models.CharField(max_length=50)
    processing_time = models.FloatField(help_text="Processing time in seconds")

    # Word analysis
    total_words = models.IntegerField()
    valid_words = models.IntegerField()
    invalid_words = models.IntegerField()
    accuracy_percentage = models.FloatField()

    # Detailed word data (stored as JSON)
    word_details = models.JSONField(
        default=list, help_text="Detailed information about each word")

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Optional: store the actual image file
    image_file = models.FileField(
        upload_to='analyzed_images/', null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Image Analysis Result"
        verbose_name_plural = "Image Analysis Results"

    def __str__(self):
        return f"Image Analysis: {self.image_name} ({self.detected_language}) - {self.accuracy_percentage:.1f}%"

    @property
    def success_rate(self):
        """Calculate success rate as a percentage"""
        if self.total_words == 0:
            return 0.0
        return (self.valid_words / self.total_words) * 100

    def get_word_summary(self):
        """Get a summary of word validation results"""
        return {
            'total': self.total_words,
            'valid': self.valid_words,
            'invalid': self.invalid_words,
            'unknown': self.total_words - self.valid_words - self.invalid_words,
            'accuracy': self.accuracy_percentage
        }

    def get_invalid_words(self):
        """Get list of invalid words with suggestions"""
        invalid_words = []
        for word_data in self.word_details:
            if word_data.get('is_valid') is False:
                invalid_words.append({
                    'text': word_data.get('text'),
                    'suggestions': word_data.get('suggestions', [])
                })
        return invalid_words

    def get_confidence_distribution(self):
        """Get distribution of confidence scores"""
        confidence_ranges = {
            'high': 0,      # 0.8-1.0
            'medium': 0,    # 0.6-0.79
            'low': 0        # 0.0-0.59
        }

        for word_data in self.word_details:
            confidence = word_data.get('confidence', 0)
            if confidence >= 0.8:
                confidence_ranges['high'] += 1
            elif confidence >= 0.6:
                confidence_ranges['medium'] += 1
            else:
                confidence_ranges['low'] += 1

        return confidence_ranges


class ImageAnalysisSession(models.Model):
    """Model to track image analysis sessions for batch processing"""

    session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )

    # Batch processing info
    total_images = models.IntegerField(default=0)
    processed_images = models.IntegerField(default=0)
    successful_images = models.IntegerField(default=0)
    failed_images = models.IntegerField(default=0)

    # Configuration used
    ocr_engine = models.CharField(max_length=50)
    preprocess_enabled = models.BooleanField(default=True)
    word_validation_enabled = models.BooleanField(default=True)

    # Results summary
    overall_accuracy = models.FloatField(null=True, blank=True)
    average_processing_time = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']
        verbose_name = "Image Analysis Session"
        verbose_name_plural = "Image Analysis Sessions"

    def __str__(self):
        return f"Session {self.session_id} - {self.status} ({self.processed_images}/{self.total_images})"

    def mark_completed(self):
        """Mark session as completed and calculate summary statistics"""
        self.completed_at = timezone.now()
        self.status = 'completed'

        # Calculate summary statistics
        results = ImageAnalysisResult.objects.filter(
            created_at__gte=self.started_at,
            created_at__lte=self.completed_at
        )

        if results.exists():
            self.overall_accuracy = results.aggregate(
                avg_accuracy=models.Avg('accuracy_percentage')
            )['avg_accuracy']

            self.average_processing_time = results.aggregate(
                avg_time=models.Avg('processing_time')
            )['avg_time']

        self.save()

    def get_session_summary(self):
        """Get a summary of the session"""
        return {
            'session_id': self.session_id,
            'status': self.status,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress': {
                'total': self.total_images,
                'processed': self.processed_images,
                'successful': self.successful_images,
                'failed': self.failed_images
            },
            'performance': {
                'overall_accuracy': self.overall_accuracy,
                'average_processing_time': self.average_processing_time
            }
        }
