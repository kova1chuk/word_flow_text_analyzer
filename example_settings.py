# Example Django settings for Image Text Analysis System
# Copy relevant sections to your actual settings.py file

# Image processing configuration
IMAGE_PROCESSING = {
    'DEFAULT_ENGINE': 'tesseract',
    'MAX_IMAGE_SIZE': 10 * 1024 * 1024,  # 10MB
    'SUPPORTED_FORMATS': ['jpeg', 'jpg', 'png', 'bmp', 'tiff'],
    'PREPROCESSING_ENABLED': True,
    'WORD_VALIDATION_ENABLED': True,
    'BATCH_PROCESSING_MAX_WORKERS': 4,
    'BATCH_PROCESSING_MAX_IMAGES': 100,
}

# Cloud API credentials (optional - only set if you want to use cloud OCR)
# Google Cloud Vision
GOOGLE_CLOUD_CREDENTIALS_PATH = '/path/to/your/google-credentials.json'

# Azure AI Vision
AZURE_VISION_KEY = 'your_azure_api_key_here'
AZURE_VISION_ENDPOINT = 'https://your-resource.cognitiveservices.azure.com/'

# AWS Textract
AWS_ACCESS_KEY_ID = 'your_aws_access_key_here'
AWS_SECRET_ACCESS_KEY = 'your_aws_secret_key_here'
AWS_DEFAULT_REGION = 'us-east-1'

# File upload settings
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Maximum file upload size (should match IMAGE_PROCESSING['MAX_IMAGE_SIZE'])
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# Logging configuration for image processing
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/image_processing.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'parser.lib.image_processor': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'parser.views.image': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Cache configuration (optional - for performance improvement)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    },
    'image_processing': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'image-processing-cache',
        'TIMEOUT': 300,  # 5 minutes
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    },
}

# Celery configuration (optional - for background processing)
# Uncomment if you want to use Celery for background image processing
"""
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Image processing tasks
CELERY_TASK_ROUTES = {
    'parser.tasks.process_image': {'queue': 'image_processing'},
    'parser.tasks.process_batch': {'queue': 'image_processing'},
}
"""

# Security settings for file uploads
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'your-domain.com']

# CORS settings (if using cross-origin requests)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://your-frontend-domain.com",
]

# Content Security Policy for file uploads
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "blob:")

# Example environment variables (set these in your .env file or system)
"""
# .env file example:
GOOGLE_CLOUD_CREDENTIALS_PATH=/path/to/google-credentials.json
AZURE_VISION_KEY=your_azure_api_key
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Or set in your shell:
export GOOGLE_CLOUD_CREDENTIALS_PATH=/path/to/google-credentials.json
export AZURE_VISION_KEY=your_azure_api_key
export AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
export AWS_ACCESS_KEY_ID=your_aws_access_key
export AWS_SECRET_ACCESS_KEY=your_aws_secret_key
export AWS_DEFAULT_REGION=us-east-1
"""

# Performance tuning
"""
# For high-volume image processing, consider these settings:

# Database connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'MIN_CONNS': 5,
        },
    }
}

# Redis for caching and session storage
REDIS_URL = 'redis://localhost:6379/0'
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Async processing with Celery
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_WORKER_CONCURRENCY = 4
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
"""
