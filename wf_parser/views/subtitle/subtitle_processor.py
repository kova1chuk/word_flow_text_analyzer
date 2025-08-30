"""
Subtitle processing library for extracting text from various subtitle formats.
"""

import re
import os
import logging
from typing import Optional, Tuple
from dataclasses import dataclass
from wf_parser.lib.base_processor import BaseProcessor, ProcessingResult


@dataclass
class SubtitleFileInfo:
    """Information about a subtitle file."""
    filename: str
    file_extension: str
    file_size: int
    content: str
    encoding: str


class SubtitleProcessor(BaseProcessor):
    """
    A comprehensive subtitle processing library for extracting text from various subtitle formats.

    This class provides methods to:
    - Validate subtitle file formats
    - Extract text from different subtitle formats (SRT, VTT, TXT)
    - Handle different encodings
    - Process subtitle content
    """

    # Supported subtitle file extensions
    SUPPORTED_EXTENSIONS = ['.srt', '.vtt', '.txt']

    def __init__(self):
        """Initialize the SubtitleProcessor."""
        super().__init__()

    def clean_html_tags(self, text: str) -> str:
        """
        Remove HTML tags from text content.

        Args:
            text (str): Text content that may contain HTML tags

        Returns:
            str: Cleaned text without HTML tags
        """
        # Remove HTML tags like <i>, <b>, <u>, etc.
        text = re.sub(r'<[^>]+>', '', text)

        # Clean up extra whitespace that might be left after tag removal
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

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

        file_extension = os.path.splitext(filename.lower())[1]

        if file_extension not in self.SUPPORTED_EXTENSIONS:
            supported_formats = ", ".join(self.SUPPORTED_EXTENSIONS)
            return False, f"Unsupported file format. Supported formats: {supported_formats}"

        return True, ""

    def read_subtitle_file(self, file_content: bytes, filename: str) -> Tuple[bool, str, Optional[SubtitleFileInfo]]:
        """
        Read and decode subtitle file content.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            Tuple[bool, str, Optional[SubtitleFileInfo]]: (success, error_message, file_info)
        """
        # Validate file extension
        is_valid, error_message = self.validate_file_extension(filename)
        if not is_valid:
            return False, error_message, None

        file_extension = os.path.splitext(filename.lower())[1]
        file_size = len(file_content)

        # Try to decode with UTF-8 first
        try:
            content = file_content.decode('utf-8')
            encoding = 'utf-8'
            self.logger.info(
                f"Successfully decoded {filename} with UTF-8 encoding")
        except UnicodeDecodeError:
            # Try with latin-1 encoding
            try:
                content = file_content.decode('latin-1')
                encoding = 'latin-1'
                self.logger.info(
                    f"Successfully decoded {filename} with latin-1 encoding")
            except Exception as decode_error:
                error_msg = f"Failed to decode subtitle file: {str(decode_error)}"
                self.logger.error(error_msg)
                return False, error_msg, None

        file_info = SubtitleFileInfo(
            filename=filename,
            file_extension=file_extension,
            file_size=file_size,
            content=content,
            encoding=encoding
        )

        return True, "", file_info

    def extract_text_from_srt(self, content: str) -> str:
        """
        Extract text content from SRT (SubRip Subtitle) format.

        Args:
            content (str): SRT file content

        Returns:
            str: Extracted text content
        """
        lines = content.split('\n')
        text_lines = []
        skip_next = False

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                skip_next = False
                continue

            # Skip if we're supposed to skip this line
            if skip_next:
                skip_next = False
                continue

            # Skip number lines (subtitle sequence numbers)
            if re.match(r'^\d+$', line):
                skip_next = True  # Skip next line (timestamp)
                continue

            # Skip timestamp lines
            if re.match(r'^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$', line):
                continue

            # This is a text line - clean HTML tags and add it
            cleaned_line = self.clean_html_tags(line)
            if cleaned_line:  # Only add non-empty lines after cleaning
                text_lines.append(cleaned_line)

        return ' '.join(text_lines)

    def extract_text_from_vtt(self, content: str) -> str:
        """
        Extract text content from VTT (WebVTT) format.

        Args:
            content (str): VTT file content

        Returns:
            str: Extracted text content
        """
        lines = content.split('\n')
        text_lines = []
        skip_next = False

        for line in lines:
            line = line.strip()

            # Skip empty lines and WEBVTT header
            if not line or line == 'WEBVTT':
                continue

            # Skip timestamp lines
            if re.match(r'^\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}', line):
                skip_next = True
                continue

            # Skip style/note lines that start with identifiers
            if skip_next and re.match(r'^[A-Za-z]+:', line):
                continue

            # Reset skip flag
            if skip_next:
                skip_next = False

            # This is a text line - clean HTML tags and add it
            cleaned_line = self.clean_html_tags(line)
            if cleaned_line:  # Only add non-empty lines after cleaning
                text_lines.append(cleaned_line)

        return ' '.join(text_lines)

    def extract_text_from_txt(self, content: str) -> str:
        """
        Extract text content from plain text format.

        Args:
            content (str): TXT file content

        Returns:
            str: Extracted text content (cleaned)
        """
        # For plain text, clean up extra whitespace and HTML tags
        lines = content.split('\n')
        text_lines = []

        for line in lines:
            line = line.strip()
            if line:  # Only process non-empty lines
                cleaned_line = self.clean_html_tags(line)
                if cleaned_line:  # Only add non-empty lines after cleaning
                    text_lines.append(cleaned_line)

        return ' '.join(text_lines)

    def extract_text_from_subtitles(self, content: str, file_extension: str) -> str:
        """
        Extract text content from subtitle file based on its format.

        Args:
            content (str): Subtitle file content
            file_extension (str): File extension (e.g., '.srt', '.vtt', '.txt')

        Returns:
            str: Extracted text content
        """
        file_extension = file_extension.lower()

        if file_extension == '.srt':
            return self.extract_text_from_srt(content)
        elif file_extension == '.vtt':
            return self.extract_text_from_vtt(content)
        elif file_extension == '.txt':
            return self.extract_text_from_txt(content)
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def process_file(self, file_content: bytes, filename: str) -> ProcessingResult:
        """
        Process a subtitle file and extract text content.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            ProcessingResult: Processing result with success status, error message, and extracted text
        """
        self.log_processing_start(filename, len(file_content))

        # Read and validate the file
        success, error_message, file_info = self.read_subtitle_file(
            file_content, filename)
        if not success:
            return self.create_error_result(error_message)

        try:
            # Extract text based on file format
            extracted_text = self.extract_text_from_subtitles(
                file_info.content,
                file_info.file_extension
            )

            # Validate that we got text content
            is_valid, error_message = self.validate_text_content(
                extracted_text)
            if not is_valid:
                return self.create_error_result(error_message)

            self.log_processing_success(filename, len(extracted_text))
            return self.create_success_result(extracted_text, file_info)

        except Exception as e:
            error_msg = f"Failed to extract text from subtitles: {str(e)}"
            self.log_processing_error(filename, error_msg)
            return self.create_error_result(error_msg)

    def process_subtitle_file(self, file_content: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Process a subtitle file and extract text content.
        Legacy method for backward compatibility.

        Args:
            file_content (bytes): Raw file content
            filename (str): Name of the file

        Returns:
            Tuple[bool, str, Optional[str]]: (success, error_message, extracted_text)
        """
        result = self.process_file(file_content, filename)
        return result.success, result.error_message, result.extracted_text
