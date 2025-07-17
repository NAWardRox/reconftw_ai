# Create example configuration
create_config() {
    if [ ! -f "config.json" ]; then
        print_status "Creating example configuration file..."
        cat > config.json << EOF
{
  "providers": {
    "ollama": {
      "default_model": "llama3:8b"
    },
    "api": {
      "url": "https://your-api-domain.com/v1/generate",
      "default_model": "fdtn-ai/Foundation-Sec-8B"
    },
    "claude": {
      "default_model": "claude-3-sonnet-20240229"
    }
  },
  "generation_defaults": {
    "max_tokens": 512,
    "temperature": 0.5
  }
}
EOF
        print_status "Configuration file created: config.json"
    else
        print_warning "config.json already exists, skipping..."
    fi
}

# Create example credentials files
create_credential_examples() {
    if [ ! -f "credentials.json.example" ]; then
        print_status "Creating example credentials file..."
        cat > credentials.json.example << EOF
{
  "api_url": "https://your-api-domain.com/v1/generate",
  "api_username": "your-username",
  "api_password": "your-password",
  "api_key": "your-api-key-if-using-bearer-token",
  "claude_api_key": "sk-ant-your-claude-api-key",
  "headers": {
    "User-Agent": "ReconFTW-AI/1.0",
    "X-Custom-Header": "your-custom-value"
  }
}
EOF
        print_status "Example credentials file created: credentials.json.example"
    else
        print_warning "credentials.json.example already exists, skipping..."
    fi
}#!/bin/bash

set -e

echo "🚀 ReconFTW-AI Installation Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3 is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d" " -f2)
        print_status "Python 3 found: $PYTHON_VERSION"
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or later."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
    else
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip3 install -r requirements.txt
    print_status "Dependencies installed successfully"
}

# Check if Ollama is installed
check_ollama() {
    if command -v ollama &> /dev/null; then
        print_status "Ollama found"
        return 0
    else
        print_warning "Ollama not found"
        return 1
    fi
}

# Install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        print_warning "On macOS, please install Ollama manually from https://ollama.ai"
    else
        print_warning "Unsupported OS. Please install Ollama manually from https://ollama.ai"
    fi
}

# Download a default model
download_model() {
    local model=${1:-"llama3:8b"}
    print_status "Downloading model: $model"
    ollama pull "$model"
    print_status "Model downloaded successfully"
}

# Create example configuration
create_config() {
    if [ ! -f "config.json" ]; then
        print_status "Creating example configuration file..."
        cat > config.json << EOF
{
  "providers": {
    "ollama": {
      "default_model": "llama3:8b"
    },
    "api": {
      "url": "https://your-api-domain.com/v1/generate",
      "default_model": "fdtn-ai/Foundation-Sec-8B"
    },
    "claude": {
      "default_model": "claude-3-sonnet-20240229"
    }
  },
  "generation_defaults": {
    "max_tokens": 512,
    "temperature": 0.5
  }
}
EOF
        print_status "Configuration file created: config.json"
    else
        print_warning "config.json already exists, skipping..."
    fi
}

# Create test data directory
create_test_data() {
    if [ ! -d "test_data" ]; then
        print_status "Creating test data directory..."
        mkdir -p test_data/{osint,subdomains,hosts,webs}

        # Create sample test files
        echo "sample OSINT data for testing" > test_data/osint/sample.txt
        echo "sample subdomain data for testing" > test_data/subdomains/sample.txt
        echo "sample host data for testing" > test_data/hosts/sample.txt
        echo "sample web data for testing" > test_data/webs/sample.txt

        print_status "Test data directory created: test_data/"
    else
        print_warning "test_data directory already exists, skipping..."
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."

    # Test with Ollama if available
    if command -v ollama &> /dev/null; then
        print_status "Testing with Ollama..."
        python3 test_api.py --provider ollama --model llama3:8b || print_warning "Ollama test failed"
    fi

    print_status "Installation test completed"
}

# Main installation process
main() {
    echo ""
    print_status "Starting installation process..."

    # Check prerequisites
    check_python
    check_pip

    # Install dependencies
    install_dependencies

    # Ask user about Ollama installation
    if ! check_ollama; then
        echo ""
        read -p "Do you want to install Ollama for local LLM support? (y/n): " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_ollama

            if command -v ollama &> /dev/null; then
                echo ""
                read -p "Do you want to download a default model (llama3:8b)? (y/n): " -n 1 -r
                echo ""
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    download_model "llama3:8b"
                fi
            fi
        fi
    fi

    # Create configuration and test data
    create_config
    create_credential_examples
    create_test_data

    # Make scripts executable
    chmod +x reconftw_ai.py
    chmod +x test_api.py

    echo ""
    print_status "Installation completed successfully! 🎉"
    echo ""
    echo "Next steps:"
    echo "1. Copy credentials.json.example to credentials.json and fill in your API details"
    echo "2. Or set environment variables: export API_URL=..., export API_USERNAME=..., etc."
    echo "3. Test your setup: python3 test_api.py --provider api --model fdtn-ai/Foundation-Sec-8B"
    echo "4. Run analysis: python3 reconftw_ai.py --provider api --results-dir test_data --report-type brief"
    echo ""
    echo "For more information, see README.md"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-ollama)
            NO_OLLAMA=true
            shift
            ;;
        --model)
            DEFAULT_MODEL="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-ollama    Skip Ollama installation"
            echo "  --model MODEL  Specify default model to download"
            echo "  --help         Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Run main installation
main