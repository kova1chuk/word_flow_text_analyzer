from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from ebooklib import epub
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import os
import logging
from io import BytesIO
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings

from .serializers import EPubUploadSerializer, SubtitleUploadSerializer

# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.


class HealthCheckView(APIView):
    """
    Health check endpoint to verify API status
    """

    @swagger_auto_schema(
        operation_description="Check the health status of the API",
        operation_summary="Health check",
        responses={
            200: openapi.Response(
                description="API is healthy",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Health status"
                        ),
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Health message"
                        ),
                        'version': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="API version"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "status": "healthy",
                        "message": "Word Flow Text Analyzer API is running",
                        "version": "v1.0.0"
                    }
                }
            )
        },
        tags=['Health'],
        operation_id='health_check'
    )
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'Word Flow Text Analyzer API is running',
            'version': 'v1.0.0'
        })


class UploadEpubView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="""
        Upload an EPUB file for parsing and text analysis.
        
        This endpoint accepts an EPUB file and returns:
        - Full word list (all words from the book)
        - Unique word list (deduplicated words)
        - List of sentences from the book
        - Statistics (total counts)
        
        The text is processed to:
        - Remove HTML tags and formatting
        - Convert to lowercase
        - Filter for alphabetic words only
        - Remove extra whitespace
        """,
        operation_summary="Upload and parse EPUB file",
        request_body=EPubUploadSerializer,
        responses={
            200: openapi.Response(
                description="EPUB file successfully parsed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'word_list': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Complete list of all words from the EPUB (lowercase, alphabetic only)"
                        ),
                        'unique_words': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Deduplicated list of unique words (sorted alphabetically)"
                        ),
                        'sentences': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of sentences extracted from the EPUB"
                        ),
                        'total_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of words in the book"
                        ),
                        'total_unique_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of unique words in the book"
                        ),
                        'total_sentences': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of sentences in the book"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "word_list": ["this", "is", "a", "test", "book", "with", "many", "words"],
                        "unique_words": ["a", "book", "is", "many", "test", "this", "with", "words"],
                        "sentences": ["This is a test book.", "It has many words."],
                        "total_words": 8,
                        "total_unique_words": 7,
                        "total_sentences": 2
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "No file provided"
                    },
                    "application/json": {
                        "error": "File must be an EPUB file"
                    }
                }
            ),
            500: openapi.Response(
                description="Internal server error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "Error processing EPUB file: Invalid EPUB format"
                    }
                }
            )
        },
        tags=['EPUB Processing'],
        operation_id='upload_epub'
    )
    def post(self, request):
        try:
            logger.info("Starting EPUB upload processing")

            # Check if file is provided
            if 'file' not in request.FILES:
                logger.error("No file provided in request")
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            epub_file = request.FILES['file']
            logger.info(
                f"Received file: {epub_file.name}, size: {epub_file.size} bytes")

            # Validate file extension
            if not epub_file.name.lower().endswith('.epub'):
                logger.error(f"Invalid file extension: {epub_file.name}")
                return Response(
                    {'error': 'File must be an EPUB file'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Ensure NLTK data is available
            try:
                logger.info("Checking NLTK punkt tokenizer")
                nltk.data.find('tokenizers/punkt')
                logger.info("NLTK punkt tokenizer is available")
            except LookupError:
                logger.info("Downloading NLTK punkt tokenizer")
                nltk.download('punkt')

            # Download all punkt resources to be safe
            try:
                nltk.download('punkt', quiet=True)
                logger.info("NLTK punkt resources downloaded")
            except Exception as e:
                logger.warning(f"Could not download punkt resources: {e}")

            # Manually download punkt_tab if needed
            try:
                nltk.download('punkt_tab', quiet=True)
                logger.info("NLTK punkt_tab downloaded")
            except Exception as e:
                logger.warning(f"Could not download punkt_tab: {e}")

            # Read and parse the EPUB file
            try:
                logger.info("Reading EPUB file")
                # Save the uploaded file temporarily and read it
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as temp_file:
                    for chunk in epub_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                # Read the EPUB from the temporary file
                book = epub.read_epub(temp_file_path)
                logger.info("EPUB file read successfully")

                # Clean up the temporary file
                os.unlink(temp_file_path)
            except Exception as epub_error:
                logger.error(f"Failed to read EPUB file: {str(epub_error)}")
                return Response(
                    {'error': f'Failed to read EPUB file: {str(epub_error)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract text from all document items
            text = ''
            try:
                logger.info("Extracting text from EPUB")
                for item in book.get_items():
                    if item.get_type() == 9:  # ITEM_DOCUMENT
                        soup = BeautifulSoup(item.get_content(), 'html.parser')
                        text += soup.get_text() + ' '
                logger.info(f"Extracted {len(text)} characters of text")
            except Exception as text_error:
                logger.error(
                    f"Failed to extract text from EPUB: {str(text_error)}")
                return Response(
                    {'error': f'Failed to extract text from EPUB: {str(text_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Check if we got any text
            if not text.strip():
                logger.error("No text content found in EPUB file")
                return Response(
                    {'error': 'No text content found in the EPUB file'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Clean and tokenize text
            try:
                logger.info("Tokenizing text")
                # Remove extra whitespace and normalize
                text = ' '.join(text.split())

                # Simple word tokenization using regex (avoid NLTK punkt dependency)
                import re
                words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

                # Get unique words (deduplicated)
                unique_words = sorted(set(words))

                # Tokenize sentences with fallback
                try:
                    sentences = sent_tokenize(text)
                except Exception as sent_error:
                    logger.warning(
                        f"NLTK sentence tokenization failed: {sent_error}")
                    # Fallback: simple sentence splitting
                    sentences = re.split(r'[.!?]+', text)
                    sentences = [s.strip() for s in sentences if s.strip()]

                # Clean sentences (remove extra whitespace)
                sentences = [s.strip() for s in sentences if s.strip()]

                logger.info(
                    f"Processing complete: {len(words)} words, {len(unique_words)} unique words, {len(sentences)} sentences")
            except Exception as tokenize_error:
                logger.error(f"Failed to tokenize text: {str(tokenize_error)}")
                return Response(
                    {'error': f'Failed to tokenize text: {str(tokenize_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "word_list": words,
                "unique_words": unique_words,
                "sentences": sentences,
                "total_words": len(words),
                "total_unique_words": len(unique_words),
                "total_sentences": len(sentences)
            })

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Unexpected error in EPUB processing: {str(e)}")
            logger.error(f"Error details: {error_details}")
            return Response(
                {
                    'error': f'Error processing EPUB file: {str(e)}',
                    'details': error_details if settings.DEBUG else 'Enable DEBUG mode for detailed error information'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TestView(APIView):
    """
    Test endpoint to verify API functionality
    """

    def get(self, request):
        return Response({
            'message': 'API is working correctly',
            'nltk_available': nltk.data.find('tokenizers/punkt') is not None,
            'endpoints': {
                'health': '/api/health/',
                'upload': '/api/upload/',
                'test': '/api/test/',
                'text': '/api/text/',
                'subtitle': '/api/subtitle/'
            }
        })

    def post(self, request):
        return Response({
            'message': 'POST request received successfully',
            'data': request.data if hasattr(request, 'data') else 'No data'
        })


class TextAnalysisView(APIView):
    """
    Analyze simple text input for word and sentence statistics
    """

    @swagger_auto_schema(
        operation_description="""
        Analyze simple text input for word and sentence statistics.
        
        This endpoint accepts plain text and returns:
        - Full word list (all words from the text)
        - Unique word list (deduplicated words)
        - List of sentences from the text
        - Statistics (total counts)
        
        The text is processed to:
        - Convert to lowercase
        - Filter for alphabetic words only
        - Remove extra whitespace
        """,
        operation_summary="Analyze simple text",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['text'],
            properties={
                'text': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="The text to analyze"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Text successfully analyzed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'word_list': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Complete list of all words from the text (lowercase, alphabetic only)"
                        ),
                        'unique_words': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Deduplicated list of unique words (sorted alphabetically)"
                        ),
                        'sentences': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of sentences extracted from the text"
                        ),
                        'total_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of words in the text"
                        ),
                        'total_unique_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of unique words in the text"
                        ),
                        'total_sentences': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of sentences in the text"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "word_list": ["this", "is", "a", "test", "text", "with", "many", "words"],
                        "unique_words": ["a", "is", "many", "test", "text", "this", "with", "words"],
                        "sentences": ["This is a test text.", "It has many words."],
                        "total_words": 8,
                        "total_unique_words": 7,
                        "total_sentences": 2
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "No text provided"
                    },
                    "application/json": {
                        "error": "Text is too short"
                    }
                }
            )
        },
        tags=['Text Analysis'],
        operation_id='analyze_text'
    )
    def post(self, request):
        try:
            logger.info("Starting text analysis")

            # Check if text is provided
            if 'text' not in request.data:
                return Response(
                    {'error': 'No text provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            text = request.data['text']

            # Validate text
            if not text or not text.strip():
                return Response(
                    {'error': 'No text provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if len(text.strip()) < 10:
                return Response(
                    {'error': 'Text is too short (minimum 10 characters)'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            logger.info(f"Analyzing text of {len(text)} characters")

            # Clean and tokenize text
            try:
                # Remove extra whitespace and normalize
                text = ' '.join(text.split())

                # Simple word tokenization using regex
                import re
                words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

                # Get unique words (deduplicated)
                unique_words = sorted(set(words))

                # Tokenize sentences with fallback
                try:
                    sentences = sent_tokenize(text)
                except Exception as sent_error:
                    logger.warning(
                        f"NLTK sentence tokenization failed: {sent_error}")
                    # Fallback: simple sentence splitting
                    sentences = re.split(r'[.!?]+', text)
                    sentences = [s.strip() for s in sentences if s.strip()]

                # Clean sentences (remove extra whitespace)
                sentences = [s.strip() for s in sentences if s.strip()]

                logger.info(
                    f"Text analysis complete: {len(words)} words, {len(unique_words)} unique words, {len(sentences)} sentences")
            except Exception as tokenize_error:
                logger.error(f"Failed to tokenize text: {str(tokenize_error)}")
                return Response(
                    {'error': f'Failed to tokenize text: {str(tokenize_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "word_list": words,
                "unique_words": unique_words,
                "sentences": sentences,
                "total_words": len(words),
                "total_unique_words": len(unique_words),
                "total_sentences": len(sentences)
            })

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Unexpected error in text analysis: {str(e)}")
            logger.error(f"Error details: {error_details}")
            return Response(
                {
                    'error': f'Error analyzing text: {str(e)}',
                    'details': error_details if settings.DEBUG else 'Enable DEBUG mode for detailed error information'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubtitleAnalysisView(APIView):
    """
    Analyze subtitle files (SRT, VTT, etc.) for word and sentence statistics
    """
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="""
        Analyze subtitle files for word and sentence statistics.
        
        This endpoint accepts subtitle files (SRT, VTT, TXT) and returns:
        - Full word list (all words from the subtitles)
        - Unique word list (deduplicated words)
        - List of sentences from the subtitles
        - Statistics (total counts)
        
        Supported formats:
        - SRT (SubRip Subtitle)
        - VTT (WebVTT)
        - TXT (plain text)
        
        The text is processed to:
        - Remove subtitle timestamps and formatting
        - Convert to lowercase
        - Filter for alphabetic words only
        - Remove extra whitespace
        """,
        operation_summary="Analyze subtitle file",
        request_body=SubtitleUploadSerializer,
        responses={
            200: openapi.Response(
                description="Subtitle file successfully analyzed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'word_list': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Complete list of all words from the subtitles (lowercase, alphabetic only)"
                        ),
                        'unique_words': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="Deduplicated list of unique words (sorted alphabetically)"
                        ),
                        'sentences': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of sentences extracted from the subtitles"
                        ),
                        'total_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of words in the subtitles"
                        ),
                        'total_unique_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of unique words in the subtitles"
                        ),
                        'total_sentences': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of sentences in the subtitles"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "word_list": ["hello", "world", "this", "is", "a", "subtitle"],
                        "unique_words": ["a", "hello", "is", "subtitle", "this", "world"],
                        "sentences": ["Hello world.", "This is a subtitle."],
                        "total_words": 6,
                        "total_unique_words": 6,
                        "total_sentences": 2
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Error message"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "No file provided"
                    },
                    "application/json": {
                        "error": "Unsupported file format"
                    }
                }
            )
        },
        tags=['Subtitle Analysis'],
        operation_id='analyze_subtitle'
    )
    def post(self, request):
        try:
            logger.info("Starting subtitle file analysis")

            # Check if file is provided
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subtitle_file = request.FILES['file']
            logger.info(
                f"Received subtitle file: {subtitle_file.name}, size: {subtitle_file.size} bytes")

            # Validate file extension
            allowed_extensions = ['.srt', '.vtt', '.txt']
            file_extension = os.path.splitext(subtitle_file.name.lower())[1]

            if file_extension not in allowed_extensions:
                return Response(
                    {'error': f'Unsupported file format. Supported formats: {", ".join(allowed_extensions)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Read and parse the subtitle file
            try:
                logger.info("Reading subtitle file")
                # Read the file content
                content = subtitle_file.read().decode('utf-8')
                logger.info(
                    f"Read {len(content)} characters from subtitle file")
            except UnicodeDecodeError:
                # Try with different encoding
                try:
                    subtitle_file.seek(0)  # Reset file pointer
                    content = subtitle_file.read().decode('latin-1')
                    logger.info("Successfully decoded with latin-1 encoding")
                except Exception as decode_error:
                    logger.error(
                        f"Failed to decode subtitle file: {str(decode_error)}")
                    return Response(
                        {'error': 'Failed to read subtitle file (encoding issue)'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Exception as read_error:
                logger.error(
                    f"Failed to read subtitle file: {str(read_error)}")
                return Response(
                    {'error': f'Failed to read subtitle file: {str(read_error)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract text from subtitle content
            try:
                logger.info("Extracting text from subtitle content")
                text = self._extract_text_from_subtitles(
                    content, file_extension)
                logger.info(f"Extracted {len(text)} characters of text")
            except Exception as text_error:
                logger.error(
                    f"Failed to extract text from subtitles: {str(text_error)}")
                return Response(
                    {'error': f'Failed to extract text from subtitles: {str(text_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Check if we got any text
            if not text.strip():
                return Response(
                    {'error': 'No text content found in the subtitle file'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Clean and tokenize text
            try:
                logger.info("Tokenizing subtitle text")
                # Remove extra whitespace and normalize
                text = ' '.join(text.split())

                # Simple word tokenization using regex
                import re
                words = re.findall(r'\b[a-zA-Z]+\b', text.lower())

                # Get unique words (deduplicated)
                unique_words = sorted(set(words))

                # Tokenize sentences with fallback
                try:
                    sentences = sent_tokenize(text)
                except Exception as sent_error:
                    logger.warning(
                        f"NLTK sentence tokenization failed: {sent_error}")
                    # Fallback: simple sentence splitting
                    sentences = re.split(r'[.!?]+', text)
                    sentences = [s.strip() for s in sentences if s.strip()]

                # Clean sentences (remove extra whitespace)
                sentences = [s.strip() for s in sentences if s.strip()]

                logger.info(
                    f"Subtitle analysis complete: {len(words)} words, {len(unique_words)} unique words, {len(sentences)} sentences")
            except Exception as tokenize_error:
                logger.error(
                    f"Failed to tokenize subtitle text: {str(tokenize_error)}")
                return Response(
                    {'error': f'Failed to tokenize subtitle text: {str(tokenize_error)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                "word_list": words,
                "unique_words": unique_words,
                "sentences": sentences,
                "total_words": len(words),
                "total_unique_words": len(unique_words),
                "total_sentences": len(sentences)
            })

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"Unexpected error in subtitle analysis: {str(e)}")
            logger.error(f"Error details: {error_details}")
            return Response(
                {
                    'error': f'Error analyzing subtitle file: {str(e)}',
                    'details': error_details if settings.DEBUG else 'Enable DEBUG mode for detailed error information'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _extract_text_from_subtitles(self, content, file_extension):
        """
        Extract text content from different subtitle formats
        """
        import re

        if file_extension == '.srt':
            # Remove SRT timestamps and formatting
            # Pattern: number, timestamp, text, empty line
            lines = content.split('\n')
            text_lines = []
            skip_next = False

            for line in lines:
                line = line.strip()
                if not line:  # Empty line
                    skip_next = False
                    continue
                if skip_next:  # Skip timestamp line
                    skip_next = False
                    continue
                if re.match(r'^\d+$', line):  # Number line
                    skip_next = True  # Skip next line (timestamp)
                    continue
                # Timestamp line
                if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line):
                    continue
                # This is a text line
                text_lines.append(line)

            return ' '.join(text_lines)

        elif file_extension == '.vtt':
            # Remove VTT timestamps and formatting
            lines = content.split('\n')
            text_lines = []
            skip_next = False

            for line in lines:
                line = line.strip()
                if not line or line == 'WEBVTT':  # Skip empty lines and header
                    continue
                # Timestamp line
                if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line):
                    skip_next = True
                    continue
                if skip_next and re.match(r'^[A-Za-z]+:', line):  # Style/note line
                    continue
                if skip_next:
                    skip_next = False
                # This is a text line
                text_lines.append(line)

            return ' '.join(text_lines)

        else:  # .txt or other plain text
            # For plain text, just return the content
            return content
