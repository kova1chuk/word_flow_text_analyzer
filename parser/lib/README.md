# Text Parser Library

A comprehensive Python library for parsing and analyzing text content. This library provides functions to extract sentences, words, and statistics from text, returning the exact data structure you need.

## Features

- **Sentence Extraction**: Extract sentences using NLTK or fallback regex method
- **Word Analysis**: Extract words and calculate usage counts
- **Statistics**: Get comprehensive text statistics
- **Flexible Configuration**: Configurable word length filters and NLTK usage
- **Type Safety**: Full type hints and dataclass support

## Installation

The library is part of the `parser` package. No additional installation required.

## Quick Start

```python
from parser.lib.text_parser import TextParser, analyze_text

# Method 1: Using the TextParser class
parser = TextParser(use_nltk=True)
result = parser.analyze_text("Your text here")

# Method 2: Using convenience function
result = analyze_text("Your text here")

# Access the results
print(f"Sentences: {result.sentences}")
print(f"Unique words: {result.unique_words}")
print(f"Total words: {result.total_words}")
print(f"Total unique words: {result.total_unique_words}")
```

## API Reference

### TextParser Class

#### Constructor
```python
TextParser(use_nltk: bool = True)
```

#### Methods

##### `analyze_text(text: str, min_word_length: int = 1) -> TextAnalysisResult`
Perform comprehensive text analysis.

**Parameters:**
- `text` (str): Text to analyze
- `min_word_length` (int): Minimum word length to include (default: 1)

**Returns:**
- `TextAnalysisResult`: Complete analysis result with sentences, unique words, and statistics

##### `extract_sentences(text: str) -> List[str]`
Extract sentences from text.

**Parameters:**
- `text` (str): Text to extract sentences from

**Returns:**
- `List[str]`: List of sentences

##### `extract_words(text: str, min_length: int = 1) -> List[str]`
Extract words from text.

**Parameters:**
- `text` (str): Text to extract words from
- `min_length` (int): Minimum word length to include (default: 1)

**Returns:**
- `List[str]`: List of words (lowercase, alphabetic only)

##### `calculate_word_counts(words: List[str]) -> List[Dict[str, any]]`
Calculate word usage counts.

**Parameters:**
- `words` (List[str]): List of words to analyze

**Returns:**
- `List[Dict[str, any]]`: List of dictionaries with 'text' and 'usage_count' keys

##### `get_text_statistics(text: str, min_word_length: int = 1) -> Dict[str, any]`
Get basic text statistics.

**Parameters:**
- `text` (str): Text to analyze
- `min_word_length` (int): Minimum word length to include (default: 1)

**Returns:**
- `Dict[str, any]`: Dictionary with statistics including averages

##### `extract_most_common_words(text: str, top_n: int = 10, min_word_length: int = 1) -> List[Dict[str, any]]`
Extract the most common words.

**Parameters:**
- `text` (str): Text to analyze
- `top_n` (int): Number of top words to return (default: 10)
- `min_word_length` (int): Minimum word length to include (default: 1)

**Returns:**
- `List[Dict[str, any]]`: List of most common words with counts

##### `extract_words_by_frequency(text: str, min_frequency: int = 2, min_word_length: int = 1) -> List[Dict[str, any]]`
Extract words that appear at least a minimum number of times.

**Parameters:**
- `text` (str): Text to analyze
- `min_frequency` (int): Minimum frequency threshold (default: 2)
- `min_word_length` (int): Minimum word length to include (default: 1)

**Returns:**
- `List[Dict[str, any]]`: List of words meeting the frequency threshold

### Convenience Functions

#### `analyze_text(text: str, use_nltk: bool = True, min_word_length: int = 1) -> TextAnalysisResult`
Convenience function to analyze text.

#### `get_text_statistics(text: str, use_nltk: bool = True, min_word_length: int = 1) -> Dict[str, any]`
Convenience function to get text statistics.

## Data Structures

### TextAnalysisResult
```python
@dataclass
class TextAnalysisResult:
    sentences: List[str]                    # List of sentences
    unique_words: List[Dict[str, any]]      # List of unique words with counts
    total_words: int                        # Total number of words
    total_unique_words: int                 # Total number of unique words
    total_sentences: int                    # Total number of sentences
```

### Word Count Format
```python
{
    "text": "word",           # The word
    "usage_count": 5          # Number of times it appears
}
```

## Examples

### Basic Text Analysis
```python
from parser.lib.text_parser import TextParser

parser = TextParser()
result = parser.analyze_text("Hello world. This is a test.")

print(result.sentences)
# Output: ['Hello world.', 'This is a test.']

print(result.unique_words)
# Output: [{'text': 'a', 'usage_count': 1}, {'text': 'hello', 'usage_count': 1}, ...]

print(result.total_words)
# Output: 6
```

### Get Statistics Only
```python
from parser.lib.text_parser import get_text_statistics

stats = get_text_statistics("Your text here")
print(stats)
# Output: {
#     'total_words': 3,
#     'total_unique_words': 3,
#     'total_sentences': 1,
#     'average_word_length': 4.33,
#     'average_sentence_length': 3.0
# }
```

### Extract Most Common Words
```python
from parser.lib.text_parser import TextParser

parser = TextParser()
common_words = parser.extract_most_common_words("text with repeated words words", top_n=3)
print(common_words)
# Output: [{'text': 'words', 'usage_count': 2}, {'text': 'text', 'usage_count': 1}, ...]
```

## Configuration

### NLTK Usage
The library can use NLTK for better sentence tokenization or fall back to regex:
```python
# Use NLTK (default)
parser = TextParser(use_nltk=True)

# Use regex only
parser = TextParser(use_nltk=False)
```

### Word Length Filtering
Filter out short words:
```python
# Only include words with 3+ characters
result = parser.analyze_text(text, min_word_length=3)
```

## Error Handling

The library includes comprehensive error handling:
- Graceful fallback from NLTK to regex sentence tokenization
- Empty text handling
- Invalid input validation

## Performance

- **NLTK Mode**: Better sentence detection, slightly slower
- **Regex Mode**: Faster, simpler sentence detection
- **Word Extraction**: Optimized regex patterns for alphabetic words only

## Integration

The library is already integrated into the Django views:
- `TextAnalysisView` uses the library for `/api/text/` endpoint
- `UploadEpubView` uses the library for EPUB processing
- `SubtitleAnalysisView` uses the library for subtitle processing

All endpoints now return the standardized format you requested:
```typescript
{
  sentences: string[];
  unique_words: { text: string; usage_count: number }[];
  total_words: number;
  total_unique_words: number;
}
``` 