# Word Flow Text Analyzer

A Django REST API for parsing EPUB files and extracting text analysis data, containerized for Cloud Run deployment.

## Features

- Upload EPUB files via REST API
- Extract full word list from EPUB content
- Generate unique (deduplicated) word list
- Extract sentences from the book
- Text cleaning and normalization
- Error handling and validation
- **Containerized deployment on Google Cloud Run**
- **CI/CD pipeline with GitHub Actions**
- **Artifact Registry for container images**

## Local Development

### Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Run Django development server:**

   ```bash
   python manage.py runserver
   ```

3. **Access the API:**
   - Base URL: `http://127.0.0.1:8000/`
   - Upload endpoint: `http://127.0.0.1:8000/api/upload/`

## Cloud Run Deployment

### Prerequisites

1. **Google Cloud SDK installed and authenticated:**

   ```bash
   gcloud auth login
   gcloud config set project word-flow-text-analyzer
   ```

2. **Docker installed and running**

3. **Artifact Registry repository created:**

   ```bash
   gcloud artifacts repositories create word-flow-repo \
     --repository-format=docker \
     --location=europe-central2 \
     --description="Word Flow Text Analyzer container repository"
   ```

### Manual Deployment

1. **Run the deployment script:**

   ```bash
   ./deploy.sh [PROJECT_ID] [REGION]
   ```

2. **Or deploy manually:**

   ```bash
   # Configure Docker for Artifact Registry
   gcloud auth configure-docker europe-central2-docker.pkg.dev
   
   # Build and push container
   docker build -t europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:latest .
   docker push europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:latest
   
   # Deploy to Cloud Run
   gcloud run deploy word-flow \
     --image europe-central2-docker.pkg.dev/word-flow-text-analyzer/word-flow-repo/word-flow:latest \
     --region europe-central2 \
     --platform managed \
     --allow-unauthenticated \
     --memory 1Gi \
     --cpu 1
   ```

### CI/CD with GitHub Actions

1. **Set up GitHub Secrets:**
   - `GCP_PROJECT_ID`: `word-flow-text-analyzer`
   - `GCP_SA_KEY`: Base64-encoded service account key JSON

2. **Push to main branch** - automatic deployment will trigger

### CI/CD with Cloud Build

1. **Enable Cloud Build API:**

   ```bash
   gcloud services enable cloudbuild.googleapis.com
   ```

2. **Set up trigger** in Google Cloud Console or use:

   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

## API Endpoints

### POST /api/upload/

Upload an EPUB file for parsing and analysis.

**Request:**

- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing an EPUB file

**Response:**

```json
{
    "word_list": ["this", "is", "a", "test", ...],
    "unique_words": ["a", "is", "test", "this", ...],
    "sentences": ["This is a test.", "Another sentence here.", ...],
    "total_words": 1500,
    "total_unique_words": 800,
    "total_sentences": 100
}
```

**Error Responses:**

- `400 Bad Request`: No file provided or invalid file type
- `500 Internal Server Error`: Error processing the EPUB file

## Testing

### Local Testing

1. **Test with no file:**

   ```bash
   curl -X POST http://127.0.0.1:8000/api/upload/
   ```

2. **Test with wrong file type:**

   ```bash
   curl -X POST -F "file=@requirements.txt" http://127.0.0.1:8000/api/upload/
   ```

3. **Test with valid EPUB file:**

   ```bash
   curl -X POST -F "file=@your_book.epub" http://127.0.0.1:8000/api/upload/
   ```

### Cloud Run Testing

Replace `YOUR_SERVICE_URL` with your actual Cloud Run service URL:

```bash
curl -X POST -F "file=@your_book.epub" https://YOUR_SERVICE_URL/api/upload/
```

## Technical Details

### Dependencies

- **Django**: Web framework
- **Django REST Framework**: API framework
- **ebooklib**: EPUB file parsing
- **BeautifulSoup**: HTML parsing
- **NLTK**: Natural language processing
- **lxml**: XML/HTML parser
- **gunicorn**: WSGI server for production

### Container Configuration

- **Base Image**: Python 3.11-slim
- **Port**: 8080 (Cloud Run requirement)
- **Memory**: 1Gi (configurable)
- **CPU**: 1 (configurable)
- **Max Instances**: 10 (configurable)
- **Timeout**: 300 seconds (5 minutes)
- **Registry**: Artifact Registry (europe-central2)
- **Repository**: `word-flow-repo`
- **Image**: `word-flow:latest`

### Environment Variables

- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Set to `*` for Cloud Run
- `SECRET_KEY`: Django secret key (auto-generated if not set)

### Text Processing

1. **EPUB Parsing**: Uses `ebooklib` to read EPUB files and extract HTML content
2. **HTML Cleaning**: Uses `BeautifulSoup` to extract plain text from HTML
3. **Tokenization**: Uses NLTK's `word_tokenize` and `sent_tokenize` for text analysis
4. **Text Cleaning**:
   - Removes extra whitespace
   - Filters for alphabetic words only
   - Converts to lowercase
   - Deduplicates words

### Error Handling

- Validates file presence
- Validates file extension (.epub)
- Handles EPUB parsing errors
- Returns appropriate HTTP status codes

## Project Structure

```
word_flow_text_analyzer/
├── backend/                 # Django project settings
│   ├── settings.py         # Django configuration
│   └── urls.py            # Main URL routing
├── epub_parser/           # Main app
│   ├── views.py          # API views
│   ├── urls.py           # App URL routing
│   └── models.py         # Database models
├── .github/workflows/     # GitHub Actions CI/CD
│   └── deploy.yml        # Deployment workflow
├── Dockerfile            # Container configuration
├── .dockerignore         # Docker ignore file
├── cloudbuild.yaml       # Cloud Build configuration
├── deploy.sh            # Manual deployment script
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## Monitoring and Logging

### Cloud Run Logs

View logs in Google Cloud Console:

```bash
gcloud logs read --service=word-flow --limit=50
```

### Performance Monitoring

- Cloud Run automatically provides metrics
- Monitor CPU, memory, and request latency
- Set up alerts for high error rates

## Security Considerations

- HTTPS enforced by Cloud Run
- No authentication required (public API)
- File size limits: 50MB
- Input validation and sanitization
- Non-root container user

## Cost Optimization

- **Scaling**: 0 to 10 instances based on demand
- **Billing**: Pay only for actual usage
- **Memory**: 1Gi allocation (adjust based on needs)
- **Region**: europe-central2 (optimized for European users)
- **Registry**: Artifact Registry (more cost-effective than Container Registry)

## Development

To add new features or modify the existing functionality:

1. Update the `UploadEpubView` in `epub_parser/views.py`
2. Add new URL patterns in `epub_parser/urls.py` if needed
3. Test locally with `python manage.py runserver`
4. Push to main branch for automatic deployment
5. Update this README with new features

## Notes

- The NLTK punkt tokenizer is automatically downloaded on first use
- The API accepts only EPUB files (.epub extension)
- Text processing includes basic cleaning and normalization
- All words are converted to lowercase for consistency
- Cloud Run automatically scales to zero when not in use
- Deployment takes ~2-3 minutes for the first build
- Using Artifact Registry in europe-central2 for better performance in Europe
