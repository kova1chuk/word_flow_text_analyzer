"""
Text parsing library for extracting sentences, words, and statistics from text content.
"""

import re
import logging
from collections import Counter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TextAnalysisResult:
    """Result of text analysis containing all extracted data."""
    sentences: List[str]
    unique_words: List[Dict[str, any]]
    total_words: int
    total_unique_words: int
    total_sentences: int


class TextParser:
    """
    A comprehensive text parsing library for extracting sentences, words, and statistics.

    This class provides methods to:
    - Extract sentences from text
    - Extract words and calculate usage counts
    - Generate comprehensive text analysis results
    """

    def __init__(self, use_nltk: bool = True):
        """
        Initialize the TextParser.

        Args:
            use_nltk (bool): Whether to use NLTK for sentence tokenization (default: True)
        """
        self.use_nltk = use_nltk
        self._ensure_nltk_available()

    def _ensure_nltk_available(self) -> None:
        """Ensure NLTK punkt tokenizer is available if NLTK is enabled."""
        if not self.use_nltk:
            return

        try:
            import nltk
            logger.info("Checking NLTK punkt tokenizer")
            nltk.data.find('tokenizers/punkt')
            logger.info("NLTK punkt tokenizer is available")
        except (ImportError, LookupError):
            logger.info("NLTK not available or punkt tokenizer not found")
            self.use_nltk = False

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text by removing extra whitespace.

        Args:
            text (str): Raw text to clean

        Returns:
            str: Cleaned and normalized text
        """
        if not text:
            return ""

        # Remove extra whitespace and normalize
        cleaned_text = ' '.join(text.split())
        return cleaned_text

    def extract_sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text using NLTK or fallback regex method.

        Args:
            text (str): Text to extract sentences from

        Returns:
            List[str]: List of sentences
        """
        if not text:
            return []

        if self.use_nltk:
            try:
                from nltk.tokenize import sent_tokenize
                sentences = sent_tokenize(text)
                logger.info(
                    f"Successfully extracted {len(sentences)} sentences using NLTK")
            except Exception as e:
                logger.warning(
                    f"NLTK sentence tokenization failed: {e}, using fallback method")
                sentences = self._extract_sentences_fallback(text)
        else:
            sentences = self._extract_sentences_fallback(text)

        # Clean sentences (remove extra whitespace)
        cleaned_sentences = [s.strip() for s in sentences if s.strip()]
        return cleaned_sentences

    def _extract_sentences_fallback(self, text: str) -> List[str]:
        """
        Fallback method for sentence extraction using regex.

        Args:
            text (str): Text to extract sentences from

        Returns:
            List[str]: List of sentences
        """
        # Simple sentence splitting using regex
        sentences = re.split(r'[.!?]+', text)
        return sentences

    def extract_words(self, text: str, min_length: int = 1) -> List[str]:
        """
        Extract words from text using multiple regex patterns that handle:
        - Normal words like "hello"
        - Hyphenated words like "state-of-the-art"
        - Contractions like "it's", "don't"
        - Words with apostrophes or hyphens in the middle
        - Unicode letters (international characters)
        - Words with numbers like "COVID-19"

        Args:
            text (str): Text to extract words from
            min_length (int): Minimum word length to include (default: 1)

        Returns:
            List[str]: List of words (lowercase)
        """
        if not text:
            return []

        # Use multiple patterns to handle different word types
        words = []

        # Pattern 1: Basic words with Unicode support
        pattern1 = r'\b[a-zA-Z\u00C0-\u017F]+\b'
        words.extend(re.findall(pattern1, text))

        # Pattern 2: Words with apostrophes (contractions) - FIXED
        pattern2 = r'\b[a-zA-Z\u00C0-\u017F]+''[a-zA-Z\u00C0-\u017F]+\b'
        words.extend(re.findall(pattern2, text))

        # Pattern 3: Words with hyphens
        pattern3 = r'\b[a-zA-Z\u00C0-\u017F]+(?:-[a-zA-Z\u00C0-\u017F]+)+\b'
        words.extend(re.findall(pattern3, text))

        # Pattern 4: Words with numbers
        pattern4 = r'\b[a-zA-Z\u00C0-\u017F]+\d+(?:-[a-zA-Z\u00C0-\u017F\d]+)*\b'
        words.extend(re.findall(pattern4, text))

        # Pattern 5: Words starting with numbers
        pattern5 = r'\b\d+[a-zA-Z\u00C0-\u017F]+(?:-[a-zA-Z\u00C0-\u017F\d]+)*\b'
        words.extend(re.findall(pattern5, text))

        # Convert to lowercase
        words = [word.lower() for word in words]

        # Filter by minimum length
        if min_length > 1:
            words = [word for word in words if len(word) >= min_length]

        return words

    def calculate_word_counts(self, words: List[str]) -> List[Dict[str, any]]:
        """
        Calculate word usage counts and return sorted list of unique words with counts.

        Args:
            words (List[str]): List of words to analyze

        Returns:
            List[Dict[str, any]]: List of dictionaries with 'text' and 'usage_count' keys
        """
        if not words:
            return []

        # Count word occurrences
        word_counts = Counter(words)

        # Create list of unique words with counts, sorted alphabetically
        unique_words_with_counts = [
            {"text": word, "usage_count": count}
            for word, count in sorted(word_counts.items())
        ]

        return unique_words_with_counts

    def analyze_text(self, text: str, min_word_length: int = 1) -> TextAnalysisResult:
        """
        Perform comprehensive text analysis.

        Args:
            text (str): Text to analyze
            min_word_length (int): Minimum word length to include (default: 1)

        Returns:
            TextAnalysisResult: Complete analysis result
        """
        if not text:
            return TextAnalysisResult(
                sentences=[],
                unique_words=[],
                total_words=0,
                total_unique_words=0,
                total_sentences=0
            )

        # Clean the text
        cleaned_text = self.clean_text(text)

        # Extract sentences
        sentences = self.extract_sentences(cleaned_text)

        # Extract words
        words = self.extract_words(cleaned_text, min_word_length)

        # Calculate word counts
        unique_words_with_counts = self.calculate_word_counts(words)

        # Create result
        result = TextAnalysisResult(
            sentences=sentences,
            unique_words=unique_words_with_counts,
            total_words=len(words),
            total_unique_words=len(unique_words_with_counts),
            total_sentences=len(sentences)
        )

        logger.info(
            f"Text analysis complete: {result.total_words} words, "
            f"{result.total_unique_words} unique words, "
            f"{result.total_sentences} sentences"
        )

        return result

    def get_text_statistics(self, text: str, min_word_length: int = 1) -> Dict[str, any]:
        """
        Get basic text statistics without full analysis.

        Args:
            text (str): Text to analyze
            min_word_length (int): Minimum word length to include (default: 1)

        Returns:
            Dict[str, any]: Dictionary with basic statistics
        """
        if not text:
            return {
                'total_words': 0,
                'total_unique_words': 0,
                'total_sentences': 0,
                'average_word_length': 0,
                'average_sentence_length': 0
            }

        # Clean the text
        cleaned_text = self.clean_text(text)

        # Extract basic data
        sentences = self.extract_sentences(cleaned_text)
        words = self.extract_words(cleaned_text, min_word_length)
        unique_words = set(words)

        # Calculate statistics
        total_words = len(words)
        total_unique_words = len(unique_words)
        total_sentences = len(sentences)

        # Calculate averages
        average_word_length = sum(
            len(word) for word in words) / total_words if total_words > 0 else 0
        average_sentence_length = total_words / \
            total_sentences if total_sentences > 0 else 0

        return {
            'total_words': total_words,
            'total_unique_words': total_unique_words,
            'total_sentences': total_sentences,
            'average_word_length': round(average_word_length, 2),
            'average_sentence_length': round(average_sentence_length, 2)
        }

    def extract_most_common_words(self, text: str, top_n: int = 10, min_word_length: int = 1) -> List[Dict[str, any]]:
        """
        Extract the most common words from text.

        Args:
            text (str): Text to analyze
            top_n (int): Number of top words to return (default: 10)
            min_word_length (int): Minimum word length to include (default: 1)

        Returns:
            List[Dict[str, any]]: List of most common words with counts
        """
        if not text:
            return []

        # Clean and extract words
        cleaned_text = self.clean_text(text)
        words = self.extract_words(cleaned_text, min_word_length)

        # Count and get most common
        word_counts = Counter(words)
        most_common = word_counts.most_common(top_n)

        # Format result
        result = [
            {"text": word, "usage_count": count}
            for word, count in most_common
        ]

        return result

    def extract_words_by_frequency(self, text: str, min_frequency: int = 2, min_word_length: int = 1) -> List[Dict[str, any]]:
        """
        Extract words that appear at least a minimum number of times.

        Args:
            text (str): Text to analyze
            min_frequency (int): Minimum frequency threshold (default: 2)
            min_word_length (int): Minimum word length to include (default: 1)

        Returns:
            List[Dict[str, any]]: List of words meeting the frequency threshold
        """
        if not text:
            return []

        # Clean and extract words
        cleaned_text = self.clean_text(text)
        words = self.extract_words(cleaned_text, min_word_length)

        # Count words
        word_counts = Counter(words)

        # Filter by frequency
        frequent_words = [
            {"text": word, "usage_count": count}
            for word, count in word_counts.items()
            if count >= min_frequency
        ]

        # Sort by frequency (descending), then alphabetically
        frequent_words.sort(key=lambda x: (-x['usage_count'], x['text']))

        return frequent_words


# Convenience functions for backward compatibility
def analyze_text(text: str, use_nltk: bool = True, min_word_length: int = 1) -> TextAnalysisResult:
    """
    Convenience function to analyze text.

    Args:
        text (str): Text to analyze
        use_nltk (bool): Whether to use NLTK for sentence tokenization
        min_word_length (int): Minimum word length to include

    Returns:
        TextAnalysisResult: Complete analysis result
    """
    parser = TextParser(use_nltk=use_nltk)
    return parser.analyze_text(text, min_word_length)


def get_text_statistics(text: str, use_nltk: bool = True, min_word_length: int = 1) -> Dict[str, any]:
    """
    Convenience function to get text statistics.

    Args:
        text (str): Text to analyze
        use_nltk (bool): Whether to use NLTK for sentence tokenization
        min_word_length (int): Minimum word length to include

    Returns:
        Dict[str, any]: Dictionary with basic statistics
    """
    parser = TextParser(use_nltk=use_nltk)
    return parser.get_text_statistics(text, min_word_length)
