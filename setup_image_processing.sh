#!/bin/bash

# Setup script for Image Text Analysis System
# This script helps install the necessary dependencies

set -e

echo "🚀 Setting up Image Text Analysis System"
echo "========================================"

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: You're not in a virtual environment."
    echo "   It's recommended to create one first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Windows: venv\\Scripts\\activate"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system dependencies
install_system_deps() {
    echo "📦 Installing system dependencies..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            echo "   Installing Tesseract via Homebrew..."
            brew install tesseract
            brew install tesseract-lang
            
            echo "   Installing OpenCV dependencies..."
            brew install opencv
        else
            echo "❌ Homebrew not found. Please install it first:"
            echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
        
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Ubuntu/Debian
            echo "   Installing Tesseract via apt..."
            sudo apt-get update
            sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
            
            echo "   Installing OpenCV dependencies..."
            sudo apt-get install -y python3-opencv libopencv-dev
            
        elif command_exists yum; then
            # CentOS/RHEL
            echo "   Installing Tesseract via yum..."
            sudo yum install -y tesseract tesseract-langpack-eng
            
            echo "   Installing OpenCV dependencies..."
            sudo yum install -y opencv opencv-devel
            
        elif command_exists dnf; then
            # Fedora
            echo "   Installing Tesseract via dnf..."
            sudo dnf install -y tesseract tesseract-langpack-eng
            
            echo "   Installing OpenCV dependencies..."
            sudo dnf install -y opencv opencv-devel
            
        else
            echo "❌ Unsupported Linux distribution. Please install Tesseract manually."
            exit 1
        fi
        
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows (Git Bash, Cygwin)
        echo "⚠️  Windows detected. Please install Tesseract manually:"
        echo "   Download from: https://github.com/UB-Mannheim/tesseract/wiki"
        echo "   Make sure to add Tesseract to your PATH"
        
    else
        echo "❌ Unsupported operating system: $OSTYPE"
        echo "   Please install Tesseract manually for your OS"
        exit 1
    fi
}

# Function to install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install core dependencies
    echo "   Installing core dependencies..."
    pip install -r requirements.txt
    
    # Install additional dependencies that might not be in requirements.txt
    echo "   Installing additional dependencies..."
    pip install opencv-python-headless  # Headless version for servers
    
    echo "✅ Python dependencies installed successfully!"
}

# Function to verify Tesseract installation
verify_tesseract() {
    echo "🔍 Verifying Tesseract installation..."
    
    if command_exists tesseract; then
        version=$(tesseract --version 2>/dev/null | head -n1)
        echo "   ✅ Tesseract found: $version"
        
        # Check available languages
        echo "   📚 Available languages:"
        tesseract --list-langs 2>/dev/null | grep -E "^[a-z]{3}$" | head -10 | tr '\n' ' '
        echo ""
        
        # Test basic functionality
        echo "   🧪 Testing Tesseract..."
        if echo "test" | tesseract stdin stdout 2>/dev/null >/dev/null; then
            echo "   ✅ Tesseract is working correctly!"
        else
            echo "   ⚠️  Tesseract test failed, but installation seems complete"
        fi
        
    else
        echo "❌ Tesseract not found in PATH"
        echo "   Please ensure Tesseract is installed and added to your PATH"
        exit 1
    fi
}

# Function to create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    
    mkdir -p media/analyzed_images
    mkdir -p logs
    mkdir -p temp
    
    echo "✅ Directories created successfully!"
}

# Function to test the installation
test_installation() {
    echo "🧪 Testing the installation..."
    
    # Test Python imports
    echo "   Testing Python imports..."
    python -c "
try:
    from PIL import Image
    print('    ✅ PIL/Pillow imported successfully')
except ImportError as e:
    print(f'    ❌ PIL/Pillow import failed: {e}')
    exit(1)

try:
    import cv2
    print(f'    ✅ OpenCV imported successfully (version {cv2.__version__})')
except ImportError as e:
    print(f'    ❌ OpenCV import failed: {e}')
    exit(1)

try:
    import pytesseract
    print('    ✅ pytesseract imported successfully')
except ImportError as e:
    print(f'    ❌ pytesseract import failed: {e}')
    exit(1)

try:
    from langdetect import detect
    print('    ✅ langdetect imported successfully')
except ImportError as e:
    print(f'    ❌ langdetect import failed: {e}')
    exit(1)

try:
    from spellchecker import SpellChecker
    print('    ✅ pyspellchecker imported successfully')
except ImportError as e:
    print(f'    ❌ pyspellchecker import failed: {e}')
    exit(1)

print('    🎉 All Python dependencies imported successfully!')
"
    
    if [ $? -eq 0 ]; then
        echo "✅ Python dependencies test passed!"
    else
        echo "❌ Python dependencies test failed!"
        exit 1
    fi
}

# Function to show next steps
show_next_steps() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo "================================"
    echo ""
    echo "📚 Next steps:"
    echo "1. Run the test script to verify everything works:"
    echo "   python test_image_processor.py"
    echo ""
    echo "2. Start the Django development server:"
    echo "   python manage.py runserver"
    echo ""
    echo "3. Test the API endpoints:"
    echo "   - Health check: http://localhost:8000/api/image/health/"
    echo "   - Upload image: http://localhost:8000/api/image/"
    echo ""
    echo "4. For cloud OCR services, configure your credentials:"
    echo "   - Copy example_settings.py to your Django settings"
    echo "   - Set environment variables for cloud APIs"
    echo ""
    echo "5. Check the README for detailed usage instructions:"
    echo "   parser/views/image/README.md"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "- If you encounter issues, check the logs in the logs/ directory"
    echo "- Ensure Tesseract is in your PATH"
    echo "- Verify all Python dependencies are installed"
    echo "- Check the README for common issues and solutions"
}

# Main setup process
main() {
    echo "Starting setup process..."
    echo ""
    
    # Install system dependencies
    install_system_deps
    
    # Install Python dependencies
    install_python_deps
    
    # Verify Tesseract
    verify_tesseract
    
    # Create directories
    create_directories
    
    # Test installation
    test_installation
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@"
