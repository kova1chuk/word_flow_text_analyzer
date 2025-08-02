# Subtitle Processing Library

A comprehensive Python library for processing and extracting text from various subtitle file formats. This library provides functions to handle SRT, VTT, and TXT subtitle files with robust error handling and encoding support.

## Features

- **Multiple Format Support**: SRT (SubRip), VTT (WebVTT), and TXT (plain text)
- **Encoding Detection**: Automatic UTF-8 and Latin-1 encoding detection
- **Robust Parsing**: Handles various subtitle file structures and edge cases
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Type Safety**: Full type hints and dataclass support

## Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| SRT | `.srt` | SubRip Subtitle format |
| VTT | `.vtt` | WebVTT format |
| TXT | `.txt` | Plain text format |

## Quick Start

```python
from parser.views.subtitle.subtitle_processor import SubtitleProcessor

# Create processor instance
processor = SubtitleProcessor()

# Process a subtitle file
with open('subtitles.srt', 'rb') as f:
    file_content = f.read()
    
success, error_message, extracted_text = processor.process_subtitle_file(
    file_content, 'subtitles.srt'
)

if success:
    print(f"Extracted text: {extracted_text}")
else:
    print(f"Error: {error_message}")
```

## API Reference

### SubtitleProcessor Class

#### Constructor
```python
SubtitleProcessor()
```

#### Methods

##### `process_subtitle_file(file_content: bytes, filename: str) -> Tuple[bool, str, Optional[str]]`
Process a subtitle file and extract text content.

**Parameters:**
- `file_content` (bytes): Raw file content
- `filename` (str): Name of the file

**Returns:**
- `Tuple[bool, str, Optional[str]]`: (success, error_message, extracted_text)

##### `validate_file_extension(filename: str) -> Tuple[bool, str]`
Validate if the file extension is supported.

**Parameters:**
- `filename` (str): Name of the file to validate

**Returns:**
- `Tuple[bool, str]`: (is_valid, error_message)

##### `read_subtitle_file(file_content: bytes, filename: str) -> Tuple[bool, str, Optional[SubtitleFileInfo]]`
Read and decode subtitle file content.

**Parameters:**
- `file_content` (bytes): Raw file content
- `filename` (str): Name of the file

**Returns:**
- `Tuple[bool, str, Optional[SubtitleFileInfo]]`: (success, error_message, file_info)

##### `extract_text_from_srt(content: str) -> str`
Extract text content from SRT format.

**Parameters:**
- `content` (str): SRT file content

**Returns:**
- `str`: Extracted text content

##### `extract_text_from_vtt(content: str) -> str`
Extract text content from VTT format.

**Parameters:**
- `content` (str): VTT file content

**Returns:**
- `str`: Extracted text content

##### `extract_text_from_txt(content: str) -> str`
Extract text content from plain text format.

**Parameters:**
- `content` (str): TXT file content

**Returns:**
- `str`: Extracted text content

##### `extract_text_from_subtitles(content: str, file_extension: str) -> str`
Extract text content from subtitle file based on its format.

**Parameters:**
- `content` (str): Subtitle file content
- `file_extension` (str): File extension (e.g., '.srt', '.vtt', '.txt')

**Returns:**
- `str`: Extracted text content

##### `get_supported_formats() -> List[str]`
Get list of supported subtitle formats.

**Returns:**
- `List[str]`: List of supported file extensions

##### `get_format_info() -> Dict[str, str]`
Get information about supported subtitle formats.

**Returns:**
- `Dict[str, str]`: Dictionary mapping extensions to format names

### Data Structures

#### SubtitleFileInfo
```python
@dataclass
class SubtitleFileInfo:
    filename: str           # Name of the file
    file_extension: str     # File extension
    file_size: int          # Size of the file in bytes
    content: str            # Decoded file content
    encoding: str           # Encoding used (utf-8 or latin-1)
```

## Examples

### Basic File Processing
```python
from parser.views.subtitle.subtitle_processor import SubtitleProcessor

processor = SubtitleProcessor()

# Process an SRT file
with open('movie.srt', 'rb') as f:
    content = f.read()

success, error, text = processor.process_subtitle_file(content, 'movie.srt')

if success:
    print(f"Extracted {len(text)} characters")
else:
    print(f"Error: {error}")
```

### Individual Format Processing
```python
from parser.views.subtitle.subtitle_processor import SubtitleProcessor

processor = SubtitleProcessor()

# Process SRT content directly
srt_content = """
1
00:00:01,000 --> 00:00:04,000
Hello world!

2
00:00:05,000 --> 00:00:08,000
This is a subtitle file.
"""

text = processor.extract_text_from_srt(srt_content)
print(text)  # Output: "Hello world! This is a subtitle file."
```

### Validation
```python
from parser.views.subtitle.subtitle_processor import SubtitleProcessor

processor = SubtitleProcessor()

# Validate file extension
is_valid, error = processor.validate_file_extension('movie.srt')
print(f"Valid: {is_valid}")  # True

is_valid, error = processor.validate_file_extension('movie.doc')
print(f"Valid: {is_valid}")  # False
print(f"Error: {error}")     # "Unsupported file format. Supported formats: .srt, .vtt, .txt"
```

### Get Supported Formats
```python
from parser.views.subtitle.subtitle_processor import SubtitleProcessor

processor = SubtitleProcessor()

# Get supported extensions
formats = processor.get_supported_formats()
print(formats)  # ['.srt', '.vtt', '.txt']

# Get format information
format_info = processor.get_format_info()
print(format_info)  # {'.srt': 'SubRip Subtitle', '.vtt': 'WebVTT', '.txt': 'Plain Text'}
```

## Convenience Functions

### `process_subtitle_file(file_content: bytes, filename: str) -> Tuple[bool, str, Optional[str]]`
Convenience function to process a subtitle file.

### `extract_text_from_subtitles(content: str, file_extension: str) -> str`
Convenience function to extract text from subtitle content.

## Error Handling

The library provides comprehensive error handling:

- **File Format Validation**: Checks if the file extension is supported
- **Encoding Detection**: Automatically tries UTF-8 and Latin-1 encodings
- **Content Validation**: Ensures extracted text is not empty
- **Detailed Error Messages**: Provides specific error information

### Common Error Scenarios

```python
# Unsupported file format
success, error, text = processor.process_subtitle_file(content, 'file.doc')
# error: "Unsupported file format. Supported formats: .srt, .vtt, .txt"

# Encoding issues
success, error, text = processor.process_subtitle_file(content, 'file.srt')
# error: "Failed to decode subtitle file: ..."

# Empty content
success, error, text = processor.process_subtitle_file(content, 'empty.srt')
# error: "No text content found in the subtitle file"
```

## Format-Specific Details

### SRT Format
- Supports sequence numbers
- Handles timestamp lines (HH:MM:SS,mmm --> HH:MM:SS,mmm)
- Skips empty lines and formatting

### VTT Format
- Supports WEBVTT header
- Handles timestamp lines (HH:MM:SS.mmm --> HH:MM:SS.mmm)
- Skips style and note lines
- Handles cue identifiers

### TXT Format
- Simple plain text processing
- Removes extra whitespace
- Preserves line breaks as spaces

## Integration

The library is integrated into the Django subtitle view:
- `SubtitleAnalysisView` uses the library for `/api/subtitle/` endpoint
- Handles file uploads and text extraction
- Integrates with the text parsing library for analysis

## Performance

- **Fast Processing**: Optimized regex patterns for format detection
- **Memory Efficient**: Processes files in chunks
- **Encoding Detection**: Quick fallback from UTF-8 to Latin-1 