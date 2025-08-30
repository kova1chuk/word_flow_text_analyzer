"""
Text processing library for analyzing plain text input.
"""

import logging
from typing import Optional, Tuple
from dataclasses import dataclass
from wf_parser.lib.base_processor import BaseProcessor, ProcessingResult


@dataclass
class TextInputInfo:
    """Information about text input."""
    text: str
    text_length: int
    cleaned_text: str


class TextProcessor(BaseProcessor):
    """
    A comprehensive text processing library for analyzing plain text input.

    This class provides methods to:
    - Validate text input
    - Clean and normalize text
    - Process text content for analysis
    """

    def __init__(self):
        """Initialize the TextProcessor."""
        super().__init__()

    def validate_file_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Validate if the text input is acceptable.
        For text processing, we don't validate file extensions since we work with raw text.

        Args:
            filename (str): Not used for text processing

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        return True, ""

    def validate_text_input(self, text: str) -> Tuple[bool, str]:
        """
        Validate if the text input is acceptable.

        Args:
            text (str): Text to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not text:
            return False, "No text provided"

        if not text.strip():
            return False, "No text provided"

        if len(text.strip()) < 10:
            return False, "Text is too short (minimum 10 characters)"

        return True, ""

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text input.

        Args:
            text (str): Raw text input

        Returns:
            str: Cleaned text
        """
        # Remove extra whitespace and normalize
        cleaned_text = ' '.join(text.split())
        return cleaned_text

    def process_text_input(self, text: str) -> Tuple[bool, str, Optional[TextInputInfo]]:
        """
        Process text input and prepare it for analysis.

        Args:
            text (str): Raw text input

        Returns:
            Tuple[bool, str, Optional[TextInputInfo]]: (success, error_message, text_info)
        """
        # Validate text input
        is_valid, error_message = self.validate_text_input(text)
        if not is_valid:
            return False, error_message, None

        try:
            # Clean the text
            cleaned_text = self.clean_text(text)
            text_length = len(text)

            text_info = TextInputInfo(
                text=text,
                text_length=text_length,
                cleaned_text=cleaned_text
            )

            self.log_processing_success("text input", text_length)

            return True, "", text_info

        except Exception as e:
            error_msg = f"Failed to process text input: {str(e)}"
            self.log_processing_error("text input", error_msg)
            return False, error_msg, None

    def process_file(self, file_content: bytes, filename: str) -> ProcessingResult:
        """
        Process a text file and extract text content.
        This method is required by the BaseProcessor interface.

        Args:
            file_content (bytes): Raw file content (text as bytes)
            filename (str): Name of the file

        Returns:
            ProcessingResult: Processing result with success status, error message, and extracted text
        """
        try:
            # Convert bytes to string
            text = file_content.decode('utf-8')

            # Process the text
            success, error_message, text_info = self.process_text_input(text)

            if not success:
                return self.create_error_result(error_message)

            return self.create_success_result(text_info.cleaned_text, text_info)

        except Exception as e:
            error_msg = f"Failed to process text file: {str(e)}"
            self.log_processing_error(filename, error_msg)
            return self.create_error_result(error_msg)
