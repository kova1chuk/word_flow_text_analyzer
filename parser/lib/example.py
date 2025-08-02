#!/usr/bin/env python3
"""
Example usage of the TextParser library.

This script demonstrates how to use the TextParser class to analyze text
and extract the values you need.
"""

from text_parser import TextParser, analyze_text, get_text_statistics


def main():
    """Demonstrate the TextParser library functionality."""

    # Sample text for analysis
    sample_text = """
    This is a sample text for analysis. It contains multiple sentences.
    The text has various words that appear multiple times. For example,
    the word 'text' appears several times in this sample.
    """

    print("=== TextParser Library Example ===\n")
    print(f"Sample text: {sample_text.strip()}\n")

    # Method 1: Using the TextParser class
    print("1. Using TextParser class:")
    parser = TextParser(use_nltk=True)
    result = parser.analyze_text(sample_text, min_word_length=1)

    print(f"   Sentences: {result.sentences}")
    print(f"   Unique words with counts: {result.unique_words}")
    print(f"   Total words: {result.total_words}")
    print(f"   Total unique words: {result.total_unique_words}")
    print(f"   Total sentences: {result.total_sentences}\n")

    # Method 2: Using convenience functions
    print("2. Using convenience functions:")
    result2 = analyze_text(sample_text, use_nltk=True, min_word_length=1)

    print(f"   Sentences: {result2.sentences}")
    print(f"   Unique words with counts: {result2.unique_words}")
    print(f"   Total words: {result2.total_words}")
    print(f"   Total unique words: {result2.total_unique_words}\n")

    # Method 3: Get basic statistics only
    print("3. Getting basic statistics:")
    stats = get_text_statistics(sample_text, use_nltk=True, min_word_length=1)

    print(f"   Statistics: {stats}\n")

    # Method 4: Extract most common words
    print("4. Most common words:")
    common_words = parser.extract_most_common_words(
        sample_text, top_n=5, min_word_length=1)
    print(f"   Top 5 words: {common_words}\n")

    # Method 5: Extract words by frequency
    print("5. Words appearing at least 2 times:")
    frequent_words = parser.extract_words_by_frequency(
        sample_text, min_frequency=2, min_word_length=1)
    print(f"   Frequent words: {frequent_words}\n")

    # Method 6: Individual methods
    print("6. Using individual methods:")
    cleaned_text = parser.clean_text(sample_text)
    sentences = parser.extract_sentences(cleaned_text)
    words = parser.extract_words(cleaned_text, min_length=1)
    word_counts = parser.calculate_word_counts(words)

    print(f"   Cleaned text: '{cleaned_text}'")
    print(f"   Sentences: {sentences}")
    print(f"   Words: {words}")
    print(f"   Word counts: {word_counts}\n")

    print("=== Example Complete ===")


if __name__ == "__main__":
    main()
