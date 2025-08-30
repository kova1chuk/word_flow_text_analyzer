# Text Processing Library

This package contains the text processing functionality for the Word Flow Text Analyzer.

## Overview

The text processing library provides comprehensive functionality for:
- Validating text input
- Cleaning and normalizing text
- Processing text content for analysis
- Analyzing plain text input

## Structure

```
text/
├── __init__.py           # Package initialization and exports
├── text_processor.py     # Core text processing logic
├── text_view.py         # Django REST API view for text analysis
└── README.md            # This documentation
```

## Components

### TextProcessor

The main processing class that handles text input operations.

**Key Methods:**
- `validate_text_input()` - Validates text input format and length
- `clean_text()` - Cleans and normalizes text input
- `process_text_input()` - Main processing method

**Usage:**
```python
from parser.views.text.text_processor import TextProcessor

# Create processor instance
processor = TextProcessor()

# Process text input
success, error_message, text_info = processor.process_text_input(text)
```

### TextAnalysisView

Django REST API view for text analysis.

**Endpoint:** `/api/text/`

**Features:**
- Accepts plain text input
- Validates text requirements
- Performs text analysis
- Returns word and sentence statistics

## Input Requirements

- **Minimum length:** 10 characters
- **Format:** Plain text
- **Content:** Any readable text content

## Dependencies

- `logging` - Logging functionality
- `typing` - Type hints
- `dataclasses` - Data structures

## Error Handling

The library provides comprehensive error handling for:
- Empty text input
- Text too short
- Invalid text format
- Processing errors
- Analysis failures

## Example Request

```json
{
    "text": "This is a sample text for analysis. It contains multiple sentences and various words."
}
```

## Example Response

```json
{
    "sentences": [
        "This is a sample text for analysis.",
        "It contains multiple sentences and various words."
    ],
    "unique_words": [
        {"text": "a", "usage_count": 1},
        {"text": "analysis", "usage_count": 1},
        {"text": "and", "usage_count": 1},
        {"text": "contains", "usage_count": 1},
        {"text": "for", "usage_count": 1},
        {"text": "is", "usage_count": 1},
        {"text": "it", "usage_count": 1},
        {"text": "multiple", "usage_count": 1},
        {"text": "sample", "usage_count": 1},
        {"text": "sentences", "usage_count": 1},
        {"text": "text", "usage_count": 1},
        {"text": "this", "usage_count": 1},
        {"text": "various", "usage_count": 1},
        {"text": "words", "usage_count": 1}
    ],
    "total_words": 14,
    "total_unique_words": 14
}
```

## Integration

This library integrates with:
- `TextParser` from `parser.lib.text_parser` for text analysis
- Django REST Framework for API endpoints
- Swagger/OpenAPI for documentation 