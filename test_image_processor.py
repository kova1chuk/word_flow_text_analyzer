#!/usr/bin/env python3
"""
Test script for the Image Text Analysis System

This script demonstrates the basic functionality of the image processor.
Make sure you have the required dependencies installed and Tesseract set up.
"""

import os
import sys
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def test_image_processor():
    """Test the basic image processor functionality"""
    try:
        from parser.lib.image_processor import ImageProcessor, OCREngine, process_image_simple

        print("🚀 Testing Image Text Analysis System")
        print("=" * 50)

        # Create processor
        print("\n1. Creating ImageProcessor...")
        processor = ImageProcessor()

        # Check available engines
        print(
            f"   Available OCR engines: {[e.value for e in processor.available_engines]}")

        if not processor.available_engines:
            print(
                "   ❌ No OCR engines available. Please install Tesseract or configure cloud APIs.")
            return False

        # Test with a sample image if available
        test_image_path = find_test_image()
        if test_image_path:
            print(f"\n2. Testing with image: {test_image_path}")

            try:
                # Process image
                result = processor.process_image(
                    image_path=test_image_path,
                    preprocess=True,
                    validate_words=True
                )

                # Display results
                print(
                    f"   ✅ Processing completed in {result.processing_time:.2f}s")
                print(
                    f"   📝 Extracted text: {result.text[:100]}{'...' if len(result.text) > 100 else ''}")
                print(f"   🌍 Detected language: {result.language}")
                print(f"   🎯 Confidence: {result.confidence:.2f}")
                print(f"   🔤 Total words: {len(result.words)}")

                # Get summary
                summary = processor.get_processing_summary(result)
                print(f"   📊 Accuracy: {summary['accuracy_percentage']:.1f}%")
                print(f"   ✅ Valid words: {summary['valid_words']}")
                print(f"   ❌ Invalid words: {summary['invalid_words']}")

                # Show some word details
                if result.words:
                    print(f"\n3. Word Analysis (first 5 words):")
                    for i, word in enumerate(result.words[:5]):
                        status = "✓" if word.is_valid else "✗" if word.is_valid is False else "?"
                        print(
                            f"   {i+1:2d}. {status} '{word.text}' (conf: {word.confidence:.2f})")
                        if word.suggestions:
                            print(
                                f"       Suggestions: {', '.join(word.suggestions[:3])}")

                # Export results
                print(f"\n4. Exporting results...")
                json_export = processor.export_results(result, "json")
                txt_export = processor.export_results(result, "txt")

                print(
                    f"   📄 JSON export length: {len(json_export)} characters")
                print(f"   📄 Text export length: {len(txt_export)} characters")

                return True

            except Exception as e:
                print(f"   ❌ Error processing image: {e}")
                return False
        else:
            print("\n2. No test image found. Creating a simple test...")

            # Test basic functionality without image
            try:
                # Test language detection
                test_text = "Hello world, this is a test of the image processing system."
                detected_lang = processor._detect_language(test_text)
                print(
                    f"   🌍 Language detection test: '{test_text[:30]}...' -> {detected_lang}")

                # Test word validation (if spell checker available)
                if hasattr(processor, 'spell_checkers'):
                    print("   🔤 Spell checker available")
                else:
                    print("   ⚠️  Spell checker not available")

                return True

            except Exception as e:
                print(f"   ❌ Error in basic tests: {e}")
                return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def find_test_image():
    """Find a test image in common locations"""
    test_locations = [
        "test_image.jpg",
        "test_image.png",
        "sample.jpg",
        "sample.png",
        "test.jpg",
        "test.png"
    ]

    for location in test_locations:
        if os.path.exists(location):
            return location

    # Check if there are any image files in current directory
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            return file

    return None


def test_health_check():
    """Test the health check functionality"""
    try:
        from parser.views.image import ImageAnalysisHealthView
        from rest_framework.test import APIRequestFactory

        print("\n🔍 Testing Health Check...")

        # Create a mock request
        factory = APIRequestFactory()
        request = factory.get('/health/')

        # Create view and call it
        view = ImageAnalysisHealthView()
        response = view.get(request)

        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.data}")
            return True
        else:
            print(
                f"   ❌ Health check failed with status {response.status_code}")
            return False

    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False


def main():
    """Main test function"""
    print("🧪 Image Text Analysis System - Test Suite")
    print("=" * 60)

    # Test basic functionality
    basic_test_passed = test_image_processor()

    # Test health check
    health_test_passed = test_health_check()

    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary")
    print("=" * 60)
    print(
        f"   Basic Functionality: {'✅ PASSED' if basic_test_passed else '❌ FAILED'}")
    print(
        f"   Health Check: {'✅ PASSED' if health_test_passed else '❌ FAILED'}")

    if basic_test_passed and health_test_passed:
        print("\n🎉 All tests passed! The system is working correctly.")
        print("\n📚 Next steps:")
        print("   1. Try uploading an image via the API")
        print("   2. Test batch processing with multiple images")
        print("   3. Configure cloud APIs for better accuracy")
        print("   4. Check the README for advanced usage examples")
    else:
        print("\n⚠️  Some tests failed. Please check the error messages above.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure Tesseract is installed and in PATH")
        print("   2. Check that all Python dependencies are installed")
        print("   3. Verify Django is properly configured")
        print("   4. Review the README for setup instructions")

    return basic_test_passed and health_test_passed


if __name__ == "__main__":
    # Set Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

    try:
        import django
        django.setup()
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Failed to initialize Django: {e}")
        print("   Please ensure you're running this from the project root directory")
        sys.exit(1)
