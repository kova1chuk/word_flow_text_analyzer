"""
EPUB processing library for extracting text from EPUB files.
"""

import os
import tempfile
import logging
from typing import Optional, Tuple
from dataclasses import dataclass
from ebooklib import epub
from bs4 import BeautifulSoup
from ...lib.base_processor import BaseProcessor, ProcessingResult


@dataclass
class EpubFileInfo:
    """Information about an EPUB file."""
    filename: str
    file_size: int
    book: epub.EpubBook
    temp_file_path: str
    title: str = ""


class EpubProcessor(BaseProcessor):
    """
    A comprehensive EPUB processing library for extracting text from EPUB files.

    This class provides methods to:
    - Validate EPUB file formats
    - Extract text from EPUB documents
    - Handle EPUB parsing and content extraction
    - Process EPUB content
    """

    def __init__(self):
        """Initialize the EpubProcessor."""
        super().__init__()

    def validate_file_extension(self, filename: str) -> Tuple[bool, str]:
        """
        Validate if the file extension is supported.

        Args:
            filename (str): Name of the file to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not filename:
            return False, "No filename provided"

        if not filename.lower().endswith('.epub'):
            return False, "File must be an EPUB file"

        return True, ""

    def read_epub_file(self, file_content: bytes, filename: str) -> Tuple[bool, str, Optional[EpubFileInfo]]:
        """
        Read and parse EPUB file content.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            Tuple[bool, str, Optional[EpubFileInfo]]: (success, error_message, file_info)
        """
        # Validate file extension
        is_valid, error_message = self.validate_file_extension(filename)
        if not is_valid:
            return False, error_message, None

        file_size = len(file_content)

        try:
            # Save the uploaded file temporarily and read it
            with tempfile.NamedTemporaryFile(delete=False, suffix='.epub') as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name

            # Read the EPUB from the temporary file
            book = epub.read_epub(temp_file_path)
            self.logger.info("EPUB file read successfully")

            # Extract title from metadata
            title = self.extract_title_from_epub(book)

            file_info = EpubFileInfo(
                filename=filename,
                file_size=file_size,
                book=book,
                temp_file_path=temp_file_path,
                title=title
            )

            return True, "", file_info

        except Exception as epub_error:
            error_msg = f"Failed to read EPUB file: {str(epub_error)}"
            self.logger.error(error_msg)
            return False, error_msg, None

    def extract_title_from_epub(self, book: epub.EpubBook) -> str:
        """
        Extract title from EPUB metadata.

        Args:
            book (epub.EpubBook): EPUB book object

        Returns:
            str: Extracted title or empty string if not found
        """
        try:
            # Try to get title from metadata
            if hasattr(book, 'metadata') and book.metadata:
                # Check for title in different metadata formats
                if 'http://purl.org/dc/elements/1.1/' in book.metadata:
                    dc_metadata = book.metadata['http://purl.org/dc/elements/1.1/']
                    if 'title' in dc_metadata:
                        title = dc_metadata['title'][0][0]
                        if title:
                            return title.strip()

                # Check for title in other metadata formats
                if 'title' in book.metadata:
                    title = book.metadata['title'][0][0]
                    if title:
                        return title.strip()

            # If no title found in metadata, try to get from filename
            return ""

        except Exception as e:
            self.logger.warning(
                f"Failed to extract title from EPUB metadata: {str(e)}")
            return ""

    def extract_text_from_epub(self, book: epub.EpubBook) -> str:
        """
        Extract text content from EPUB book.

        Args:
            book (epub.EpubBook): EPUB book object

        Returns:
            str: Extracted text content
        """
        text = ''

        for item in book.get_items():
            if item.get_type() == 9:  # ITEM_DOCUMENT
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text += soup.get_text() + ' '

        return text

    def process_file(self, file_content: bytes, filename: str) -> ProcessingResult:
        """
        Process an EPUB file and extract text content.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            ProcessingResult: Processing result with success status, error message, and extracted text
        """
        self.log_processing_start(filename, len(file_content))

        # Read and validate the file
        success, error_message, file_info = self.read_epub_file(
            file_content, filename)
        if not success:
            return self.create_error_result(error_message)

        try:
            # Extract text from EPUB
            extracted_text = self.extract_text_from_epub(file_info.book)

            # Clean up the temporary file
            try:
                os.unlink(file_info.temp_file_path)
            except Exception as cleanup_error:
                self.logger.warning(
                    f"Failed to clean up temporary file: {str(cleanup_error)}")

            # Validate that we got text content
            is_valid, error_message = self.validate_text_content(
                extracted_text)
            if not is_valid:
                return self.create_error_result(error_message)

            self.log_processing_success(filename, len(extracted_text))
            return self.create_success_result(extracted_text, file_info)

        except Exception as e:
            # Clean up the temporary file on error
            try:
                os.unlink(file_info.temp_file_path)
            except:
                pass

            error_msg = f"Failed to extract text from EPUB: {str(e)}"
            self.log_processing_error(filename, error_msg)
            return self.create_error_result(error_msg)

    def process_epub_file(self, file_content: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Process an EPUB file and extract text content.
        Legacy method for backward compatibility.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            Tuple[bool, str, Optional[str]]: (success, error_message, extracted_text)
        """
        result = self.process_file(file_content, filename)
        return result.success, result.error_message, result.extracted_text
