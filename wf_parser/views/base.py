from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings
import logging
import nltk
from nltk.tokenize import sent_tokenize

# Set up logging
logger = logging.getLogger(__name__)

# Ensure NLTK data is available


def ensure_nltk_data():
    """Ensure NLTK punkt tokenizer is available"""
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


def tokenize_sentences(text):
    """Tokenize text into sentences with fallback"""
    try:
        sentences = sent_tokenize(text)
    except Exception as sent_error:
        logger.warning(f"NLTK sentence tokenization failed: {sent_error}")
        # Fallback: simple sentence splitting
        import re
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

    # Clean sentences (remove extra whitespace)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences
