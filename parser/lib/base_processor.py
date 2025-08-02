"""
Abstract base class for all file processors in the Word Flow Text Analyzer.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessingResult:
    """Base class for processing results."""
    success: bool
    error_message: str
    extracted_text: Optional[str] = None
    file_info: Optional[Any] = None


class BaseProcessor(ABC):
    """
    Abstract base class for all file processors.

    This class defines the common interface and shared functionality
    for TextProcessor, SubtitleProcessor, and EpubProcessor.
    """

    def __init__(self):
        """Initialize the base processor."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def validate_file_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Validate if the file extension is supported.

        Args:
            filename (str): Name of the file to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        pass

    @abstractmethod
    def process_file(self, file_content: bytes, filename: str) -> ProcessingResult:
        """
        Process a file and extract text content.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            ProcessingResult: Processing result with success status, error message, and extracted text
        """
        pass

    def log_processing_start(self, filename: str, file_size: int) -> None:
        """
        Log the start of file processing.

        Args:
            filename (str): Name of the file being processed
            file_size (int): Size of the file in bytes
        """
        self.logger.info(f"Starting to process {filename} ({file_size} bytes)")

    def log_processing_success(self, filename: str, text_length: int) -> None:
        """
        Log successful file processing.

        Args:
            filename (str): Name of the file that was processed
            text_length (int): Length of extracted text
        """
        self.logger.info(
            f"Successfully processed {filename}, extracted {text_length} characters")

    def log_processing_error(self, filename: str, error: str) -> None:
        """
        Log file processing error.

        Args:
            filename (str): Name of the file that failed to process
            error (str): Error message
        """
        self.logger.error(f"Failed to process {filename}: {error}")

    def create_success_result(self, extracted_text: str, file_info: Optional[Any] = None) -> ProcessingResult:
        """
        Create a successful processing result.

        Args:
            extracted_text (str): Extracted text content
            file_info (Optional[Any]): Additional file information

        Returns:
            ProcessingResult: Success result
        """
        return ProcessingResult(
            success=True,
            error_message="",
            extracted_text=extracted_text,
            file_info=file_info
        )

    def create_error_result(self, error_message: str) -> ProcessingResult:
        """
        Create an error processing result.

        Args:
            error_message (str): Error message

        Returns:
            ProcessingResult: Error result
        """
        return ProcessingResult(
            success=False,
            error_message=error_message,
            extracted_text=None,
            file_info=None
        )

    def validate_text_content(self, text: str) -> Tuple[bool, str]:
        """
        Validate that extracted text has content.

        Args:
            text (str): Extracted text to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not text or not text.strip():
            return False, "No text content found in the file"
        return True, ""
