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

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Create your views here.


class UploadEpubView(APIView):
    parser_classes = [MultiPartParser]

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
