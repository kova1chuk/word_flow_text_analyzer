"""
Abstract base class for all analysis views in the Word Flow Text Analyzer.
"""

from abc import ABC, abstractmethod
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
import logging
import traceback
from .text_parser import TextParser

logger = logging.getLogger(__name__)


class BaseAnalysisView(APIView, ABC):
    """
    Abstract base class for all analysis views.

    This class provides common functionality for:
    - Text analysis using TextParser
    - Standardized response format
    - Error handling
    - Logging
    """

    def __init__(self, *args, **kwargs):
        """Initialize the base analysis view."""
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def get_processor(self):
        """
        Get the processor instance for this view.

        Returns:
            BaseProcessor: Processor instance
        """
        pass

    @abstractmethod
    def extract_text_from_request(self, request):
        """
        Extract text content from the request.

        Args:
            request: Django request object

        Returns:
            str: Extracted text content
        """
        pass

    @abstractmethod
    def get_swagger_schema(self):
        """
        Get the Swagger schema for this view.

        Returns:
            dict: Swagger schema configuration
        """
        pass

    def analyze_text(self, text: str, endpoint_type: str = "text", file_info=None, filename: str = "", custom_title: str = "") -> Response:
        """
        Analyze text content and return standardized response.

        Args:
            text (str): Text content to analyze
            endpoint_type (str): Type of endpoint for title extraction
            file_info: Additional file information (for EPUB metadata)
            filename (str): Filename for subtitle title extraction
            custom_title (str): Custom title for text endpoint

        Returns:
            Response: Standardized analysis response
        """
        try:
            self.logger.info("Analyzing text")
            parser = TextParser(use_nltk=True)
            result = parser.analyze_text(text, min_word_length=1)

            self.logger.info(
                f"Text analysis complete: {result.total_words} words, "
                f"{result.total_unique_words} unique words, "
                f"{result.total_sentences} sentences"
            )

            return self.create_analysis_response(result, text, endpoint_type, file_info, filename, custom_title)

        except Exception as analysis_error:
            self.logger.error(f"Failed to analyze text: {str(analysis_error)}")
            return Response(
                {'error': f'Failed to analyze text: {str(analysis_error)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create_analysis_response(self, result, text: str = "", endpoint_type: str = "text", file_info=None, filename: str = "", custom_title: str = "") -> Response:
        """
        Create standardized analysis response with title extraction.

        Args:
            result: TextParser analysis result
            text: Original text content for title extraction
            endpoint_type: Type of endpoint ("text", "subtitle", "epub")
            file_info: Additional file information (for EPUB metadata)
            filename (str): Filename for subtitle title extraction
            custom_title (str): Custom title for text endpoint

        Returns:
            Response: Standardized response with analysis data and title
        """
        # Extract title based on endpoint type
        title = self.extract_title(
            text, endpoint_type, result.sentences, file_info, filename, custom_title)

        return Response({
            "title": title,
            "words": [[word["text"], word["usage_count"]] for word in result.unique_words],
            "sentences": result.sentences,
            "total_words": result.total_words,
            "total_unique_words": result.total_unique_words,
            "total_sentences": result.total_sentences
        })

    def extract_title(self, text: str, endpoint_type: str, sentences: list, file_info=None, filename: str = "", custom_title: str = "") -> str:
        """
        Extract title from text based on endpoint type.

        Args:
            text: Original text content
            endpoint_type: Type of endpoint ("text", "subtitle", "epub")
            sentences: List of extracted sentences
            file_info: Additional file information (for EPUB metadata)
            filename (str): Filename for subtitle title extraction
            custom_title (str): Custom title for text endpoint

        Returns:
            str: Extracted title
        """
        if not text:
            return "Untitled"

        # For EPUB files, try to get title from metadata first
        if endpoint_type == "epub" and file_info and hasattr(file_info, 'title') and file_info.title:
            return file_info.title

        # For text endpoint, use custom title or first sentence as title
        if endpoint_type == "text":
            # Use custom title if provided
            if custom_title and custom_title.strip():
                return custom_title.strip()
            # Otherwise use first sentence as title
            if sentences:
                # Use first sentence as title, limit to reasonable length
                title = sentences[0].strip()
                if len(title) > 100:
                    title = title[:97] + "..."
                return title
            return "Untitled"

        # For subtitle files, try to extract title from filename or first subtitle
        elif endpoint_type == "subtitle":
            # Use filename as title, remove extension
            if filename:
                import os
                title = os.path.splitext(filename)[0]  # Remove file extension
                return title
            # Fallback to first meaningful subtitle if no filename
            for sentence in sentences:
                if sentence and len(sentence.strip()) > 10:  # Skip very short subtitles
                    title = sentence.strip()
                    if len(title) > 100:
                        title = title[:97] + "..."
                    return title
            return "Untitled Subtitle"

        # For EPUB files, try to extract title from metadata or first chapter
        elif endpoint_type == "epub":
            # Try to get title from first meaningful sentence
            for sentence in sentences:
                if sentence and len(sentence.strip()) > 10:  # Skip very short sentences
                    title = sentence.strip()
                    if len(title) > 100:
                        title = title[:97] + "..."
                    return title
            return "Untitled Book"

        return "Untitled"

    def handle_processing_error(self, error: Exception, context: str = "processing") -> Response:
        """
        Handle processing errors with standardized error response.

        Args:
            error (Exception): The error that occurred
            context (str): Context for the error (e.g., "processing", "analysis")

        Returns:
            Response: Error response
        """
        self.logger.error(f"Failed to {context}: {str(error)}")
        return Response(
            {'error': f'Failed to {context}: {str(error)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    def handle_unexpected_error(self, error: Exception, context: str = "analysis") -> Response:
        """
        Handle unexpected errors with detailed logging.

        Args:
            error (Exception): The unexpected error
            context (str): Context for the error

        Returns:
            Response: Error response with optional debug details
        """
        error_details = traceback.format_exc()
        self.logger.error(f"Unexpected error in {context}: {str(error)}")
        self.logger.error(f"Error details: {error_details}")

        return Response(
            {
                'error': f'Error in {context}: {str(error)}',
                'details': error_details if settings.DEBUG else 'Enable DEBUG mode for detailed error information'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    @classmethod
    def get_standard_swagger_responses(cls):
        """
        Get standard Swagger response schemas.

        Returns:
            dict: Standard response schemas
        """
        return {
            200: openapi.Response(
                description="File successfully analyzed",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'title': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Extracted title from the content"
                        ),
                        'words': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=[
                                    openapi.Schema(
                                        type=openapi.TYPE_STRING, description="The unique word"),
                                    openapi.Schema(
                                        type=openapi.TYPE_INTEGER, description="Number of times this word appears")
                                ],
                                min_items=2,
                                max_items=2
                            ),
                            description="List of unique words with their usage counts as [word, count] arrays (sorted alphabetically)"
                        ),
                        'sentences': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            description="List of sentences extracted from the content"
                        ),
                        'total_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of words"
                        ),
                        'total_unique_words': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of unique words"
                        ),
                        'total_sentences': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of sentences"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "title": "This is a test.",
                        "words": [
                            ["a", 1],
                            ["is", 1],
                            ["many", 1],
                            ["test", 1],
                            ["this", 1],
                            ["with", 1],
                            ["words", 1]
                        ],
                        "sentences": ["This is a test.", "It has many words."],
                        "total_words": 7,
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
                        "error": "Invalid file format"
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
                        ),
                        'details': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Detailed error information (only in DEBUG mode)"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "error": "Error processing file: Invalid format"
                    }
                }
            )
        }
