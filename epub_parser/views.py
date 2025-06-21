from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from ebooklib import epub
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

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
        manual_parameters=[
            openapi.Parameter(
                name='file',
                in_=openapi.IN_FORM,
                description="EPUB file to upload and parse",
                type=openapi.TYPE_FILE,
                required=True,
            ),
        ],
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
            # Check if file is provided
            if 'file' not in request.FILES:
                return Response(
                    {'error': 'No file provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            epub_file = request.FILES['file']

            # Validate file extension
            if not epub_file.name.lower().endswith('.epub'):
                return Response(
                    {'error': 'File must be an EPUB file'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Read and parse the EPUB file
            book = epub.read_epub(epub_file)

            # Extract text from all document items
            text = ''
            for item in book.get_items():
                if item.get_type() == 9:  # ITEM_DOCUMENT
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    text += soup.get_text() + ' '

            # Clean and tokenize text
            # Remove extra whitespace and normalize
            text = ' '.join(text.split())

            # Tokenize words and sentences
            words = word_tokenize(text)
            # Filter for alphabetic words only and convert to lowercase
            words = [w.lower() for w in words if w.isalpha()]

            # Get unique words (deduplicated)
            unique_words = sorted(set(words))

            # Tokenize sentences
            sentences = sent_tokenize(text)
            # Clean sentences (remove extra whitespace)
            sentences = [s.strip() for s in sentences if s.strip()]

            return Response({
                "word_list": words,
                "unique_words": unique_words,
                "sentences": sentences,
                "total_words": len(words),
                "total_unique_words": len(unique_words),
                "total_sentences": len(sentences)
            })

        except Exception as e:
            return Response(
                {'error': f'Error processing EPUB file: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
