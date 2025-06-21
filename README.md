# Word Flow Text Analyzer

A Django REST API for parsing EPUB files and extracting text analysis data.

## Features

- Upload EPUB files via REST API
- Extract full word list from EPUB content
- Generate unique (deduplicated) word list
- Extract sentences from the book
- Text cleaning and normalization
- Error handling and validation

## Setup

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

### Using curl

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

### Using Python requests

```python
import requests

# Upload an EPUB file
with open('your_book.epub', 'rb') as f:
    files = {'file': ('book.epub', f, 'application/epub+zip')}
    response = requests.post('http://127.0.0.1:8000/api/upload/', files=files)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total words: {data['total_words']}")
        print(f"Unique words: {data['total_unique_words']}")
        print(f"Sentences: {data['total_sentences']}")
    else:
        print(f"Error: {response.json()}")
```

## Technical Details

### Dependencies

- **Django**: Web framework
- **Django REST Framework**: API framework
- **ebooklib**: EPUB file parsing
- **BeautifulSoup**: HTML parsing
- **NLTK**: Natural language processing
- **lxml**: XML/HTML parser

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
├── requirements.txt       # Python dependencies
└── manage.py             # Django management script
```

## Development

To add new features or modify the existing functionality:

1. Update the `UploadEpubView` in `epub_parser/views.py`
2. Add new URL patterns in `epub_parser/urls.py` if needed
3. Test with curl or the provided test script
4. Update this README with new features

## Notes

- The NLTK punkt tokenizer is automatically downloaded on first use
- The API accepts only EPUB files (.epub extension)
- Text processing includes basic cleaning and normalization
- All words are converted to lowercase for consistency 