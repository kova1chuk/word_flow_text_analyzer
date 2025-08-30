# EPUB Processing Library

This package contains the EPUB processing functionality for the Word Flow Text Analyzer.

## Overview

The EPUB processing library provides comprehensive functionality for:
- Validating EPUB file formats
- Extracting text content from EPUB files
- Processing EPUB content for text analysis
- Handling EPUB parsing and content extraction

## Structure

```
epub/
├── __init__.py           # Package initialization and exports
├── epub_processor.py     # Core EPUB processing logic
├── epub_view.py         # Django REST API view for EPUB analysis
└── README.md            # This documentation
```

## Components

### EpubProcessor

The main processing class that handles EPUB file operations.

**Key Methods:**
- `validate_file_extension()` - Validates EPUB file format
- `read_epub_file()` - Reads and parses EPUB files
- `extract_text_from_epub()` - Extracts text content from EPUB
- `process_epub_file()` - Main processing method

**Usage:**
```python
from parser.views.epub.epub_processor import EpubProcessor

# Create processor instance
processor = EpubProcessor()

# Process EPUB file
success, error_message, text = processor.process_epub_file(file_content, filename)
```

### EpubAnalysisView

Django REST API view for EPUB file analysis.

**Endpoint:** `/api/upload/`

**Features:**
- Accepts EPUB file uploads
- Extracts text content
- Performs text analysis
- Returns word and sentence statistics

## Supported Formats

- **EPUB** - Electronic Publication format

## Dependencies

- `ebooklib` - EPUB file parsing
- `beautifulsoup4` - HTML content extraction
- `tempfile` - Temporary file handling
- `os` - File system operations

## Error Handling

The library provides comprehensive error handling for:
- Invalid file formats
- Corrupted EPUB files
- File reading errors
- Text extraction failures
- Temporary file cleanup

## Example Response

```json
{
    "word_list": ["this", "is", "a", "test", "book"],
    "unique_words": ["a", "book", "is", "test", "this"],
    "sentences": ["This is a test book."],
    "total_words": 5,
    "total_unique_words": 5,
    "total_sentences": 1
}
```

## Integration

This library integrates with:
- `TextParser` from `parser.lib.text_parser` for text analysis
- Django REST Framework for API endpoints
- Swagger/OpenAPI for documentation 