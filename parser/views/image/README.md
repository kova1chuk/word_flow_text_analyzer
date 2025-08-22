# Image Text Analysis System

This module provides comprehensive image text analysis capabilities including OCR (Optical Character Recognition), language detection, and word validation.

## Features

- **Multi-Engine OCR Support**: Tesseract (open-source), Google Cloud Vision, Azure AI Vision, AWS Textract
- **Automatic Language Detection**: Identifies the language of extracted text
- **Word Validation**: Checks each word against language dictionaries and provides suggestions
- **Image Preprocessing**: Automatic image enhancement for better OCR results
- **Batch Processing**: Process multiple images concurrently with progress tracking
- **REST API**: Full REST API with Swagger documentation
- **Result Persistence**: Store and retrieve analysis results from database

## Architecture

### Core Components

1. **ImageProcessor**: Main class that orchestrates the entire process
2. **OCR Engines**: Multiple OCR backends for different use cases
3. **Language Detection**: Automatic language identification
4. **Word Validation**: Dictionary-based word checking with suggestions
5. **Image Preprocessing**: OpenCV-based image enhancement

### OCR Engines

| Engine | Type | Accuracy | Cost | Setup Complexity |
|--------|------|----------|------|------------------|
| Tesseract | Open-source | Good | Free | Low |
| Google Vision | Cloud API | Excellent | Pay-per-use | Medium |
| Azure Vision | Cloud API | Excellent | Pay-per-use | Medium |
| AWS Textract | Cloud API | Excellent | Pay-per-use | Medium |

## Installation

### Prerequisites

1. **Python Dependencies**: Install from requirements.txt
2. **Tesseract**: For local OCR processing
3. **Cloud Credentials**: For cloud-based OCR services (optional)

### Tesseract Installation

#### macOS
```bash
brew install tesseract
brew install tesseract-lang  # For additional languages
```

#### Ubuntu/Debian
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-[lang]  # Replace [lang] with language code
```

#### Windows
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Cloud API Setup

#### Google Cloud Vision
1. Create a Google Cloud project
2. Enable Vision API
3. Create service account and download credentials JSON
4. Set environment variable: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json`

#### Azure AI Vision
1. Create Azure Cognitive Services resource
2. Get endpoint URL and API key
3. Set environment variables:
   - `AZURE_VISION_KEY=your_api_key`
   - `AZURE_VISION_ENDPOINT=your_endpoint_url`

#### AWS Textract
1. Create AWS account
2. Create IAM user with Textract permissions
3. Set environment variables:
   - `AWS_ACCESS_KEY_ID=your_access_key`
   - `AWS_SECRET_ACCESS_KEY=your_secret_key`
   - `AWS_DEFAULT_REGION=your_region`

## Usage

### Basic Usage

```python
from parser.lib.image_processor import ImageProcessor, OCREngine

# Create processor
processor = ImageProcessor()

# Process single image
result = processor.process_image(
    image_path='path/to/image.jpg',
    engine=OCREngine.TESSERACT,
    preprocess=True,
    validate_words=True
)

# Get results
print(f"Extracted text: {result.text}")
print(f"Language: {result.language}")
print(f"Confidence: {result.confidence}")

# Get summary
summary = processor.get_processing_summary(result)
print(f"Accuracy: {summary['accuracy_percentage']:.1f}%")
```

### Advanced Usage with Cloud APIs

```python
# Initialize with cloud credentials
processor = ImageProcessor(
    preferred_engine=OCREngine.GOOGLE_VISION,
    google_credentials_path='/path/to/credentials.json'
)

# Process image
result = processor.process_image(
    image_path='path/to/image.jpg',
    engine=OCREngine.GOOGLE_VISION
)
```

### Batch Processing

```python
# Process multiple images
image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
results = []

for image_path in image_paths:
    result = processor.process_image(image_path)
    results.append(result)

# Analyze batch results
total_accuracy = sum(r.confidence for r in results) / len(results)
print(f"Average accuracy: {total_accuracy:.2f}")
```

## API Endpoints

### Single Image Analysis

**POST** `/api/image/`

Process a single image with OCR, language detection, and word validation.

**Parameters:**
- `image` (file): Image file to analyze
- `engine` (string): OCR engine to use (optional, default: tesseract)
- `preprocess` (boolean): Enable image preprocessing (optional, default: true)
- `validate_words` (boolean): Enable word validation (optional, default: true)
- `export_format` (string): Export format (json, txt) (optional, default: json)

**Response:**
```json
{
  "success": true,
  "data": {
    "text": "Extracted text from image",
    "language": "en",
    "confidence": 0.85,
    "engine": "tesseract",
    "processing_time": 1.23,
    "summary": {
      "total_words": 25,
      "valid_words": 22,
      "invalid_words": 3,
      "accuracy_percentage": 88.0
    },
    "words": [
      {
        "text": "Hello",
        "confidence": 0.95,
        "is_valid": true,
        "suggestions": []
      }
    ]
  }
}
```

### Batch Image Processing

**POST** `/api/image/batch/`

Process multiple images in batch with progress tracking.

**Parameters:**
- `images` (files): List of image files
- `engine` (string): OCR engine to use (optional)
- `preprocess` (boolean): Enable preprocessing (optional)
- `validate_words` (boolean): Enable word validation (optional)
- `session_name` (string): Custom session name (optional)

**Response:**
```json
{
  "success": true,
  "session_id": "uuid-string",
  "message": "Batch processing started",
  "total_images": 5
}
```

### Batch Status Check

**GET** `/api/image/batch/status/?session_id={session_id}`

Check the status of a batch processing session.

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "uuid-string",
    "status": "processing",
    "progress": {
      "total": 5,
      "processed": 3,
      "successful": 2,
      "failed": 1
    }
  }
}
```

### Health Check

**GET** `/api/image/health/`

Check the health and availability of image analysis services.

**Response:**
```json
{
  "success": true,
  "data": {
    "available_engines": ["tesseract", "google_vision"],
    "tesseract_available": true,
    "cloud_apis_available": true,
    "spell_checkers_available": true,
    "language_detection_available": true
  }
}
```

## Configuration

### Django Settings

Add these settings to your Django settings file:

```python
# Image processing settings
IMAGE_PROCESSING = {
    'DEFAULT_ENGINE': 'tesseract',
    'MAX_IMAGE_SIZE': 10 * 1024 * 1024,  # 10MB
    'SUPPORTED_FORMATS': ['jpeg', 'jpg', 'png', 'bmp', 'tiff'],
    'PREPROCESSING_ENABLED': True,
    'WORD_VALIDATION_ENABLED': True,
}

# Cloud API credentials (optional)
GOOGLE_CLOUD_CREDENTIALS_PATH = '/path/to/google-credentials.json'
AZURE_VISION_KEY = 'your_azure_key'
AZURE_VISION_ENDPOINT = 'your_azure_endpoint'
AWS_ACCESS_KEY_ID = 'your_aws_key'
AWS_SECRET_ACCESS_KEY = 'your_aws_secret'
AWS_DEFAULT_REGION = 'us-east-1'
```

### Environment Variables

```bash
# Google Cloud Vision
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Azure AI Vision
export AZURE_VISION_KEY=your_api_key
export AZURE_VISION_ENDPOINT=your_endpoint_url

# AWS Textract
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=your_region
```

## Performance Optimization

### Image Preprocessing

The system automatically applies several preprocessing steps:
1. **Grayscale conversion** for better OCR accuracy
2. **Noise reduction** using Non-Local Means algorithm
3. **Thresholding** for binary image creation
4. **Morphological operations** for text cleanup

### Batch Processing

- **Concurrent processing** using ThreadPoolExecutor
- **Configurable worker count** (default: min(4, image_count))
- **Progress tracking** with real-time updates
- **Session management** for result organization

### Caching

- **Spell checker instances** are cached per language
- **OCR engine initialization** is done once per processor
- **Image preprocessing** results can be cached (future enhancement)

## Error Handling

### Common Issues

1. **Tesseract not found**: Install Tesseract and ensure it's in PATH
2. **Image format not supported**: Check supported formats in settings
3. **Cloud API errors**: Verify credentials and API quotas
4. **Memory issues**: Reduce image size or batch size

### Error Responses

```json
{
  "success": false,
  "error": "Detailed error message"
}
```

## Testing

### Unit Tests

```bash
python manage.py test parser.tests.test_image_processor
```

### Integration Tests

```bash
python manage.py test parser.tests.test_image_views
```

### Manual Testing

1. **Health Check**: Verify all services are available
2. **Single Image**: Test with various image types and qualities
3. **Batch Processing**: Test with multiple images
4. **Error Handling**: Test with invalid inputs

## Monitoring and Logging

### Log Levels

- **INFO**: Normal operation events
- **WARNING**: Non-critical issues
- **ERROR**: Processing failures
- **DEBUG**: Detailed debugging information

### Key Metrics

- Processing time per image
- OCR confidence scores
- Word validation accuracy
- Batch processing throughput
- Error rates by engine

## Troubleshooting

### Tesseract Issues

```bash
# Check Tesseract installation
tesseract --version

# Check available languages
tesseract --list-langs

# Test OCR manually
tesseract test_image.png stdout
```

### Cloud API Issues

1. **Check credentials**: Verify API keys and endpoints
2. **Check quotas**: Ensure API usage limits aren't exceeded
3. **Check network**: Verify internet connectivity
4. **Check permissions**: Ensure proper IAM roles/permissions

### Performance Issues

1. **Reduce image size**: Compress images before processing
2. **Use appropriate engine**: Cloud APIs for high accuracy, Tesseract for cost
3. **Adjust batch size**: Balance between speed and resource usage
4. **Enable preprocessing**: Usually improves OCR accuracy

## Future Enhancements

1. **Advanced preprocessing**: Machine learning-based image enhancement
2. **Custom dictionaries**: User-defined word lists for validation
3. **Result caching**: Cache OCR results for repeated images
4. **Webhook support**: Notify external systems of completion
5. **Real-time processing**: WebSocket-based progress updates
6. **Mobile optimization**: Lightweight processing for mobile devices

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review logs for error details
3. Test with simple images first
4. Verify all dependencies are installed
5. Check cloud API quotas and billing
