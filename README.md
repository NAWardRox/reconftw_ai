# ReconFTW-AI

**AI-powered analysis tool for ReconFTW penetration testing results**

Transform your ReconFTW reconnaissance outputs into actionable security reports using local or cloud-based LLM providers.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Credentials
Choose one method:

**Option A: Environment Variables**
```bash
export API_URL="https://your-api-domain.com/v1/generate"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
```

**Option B: Create credentials.json**
```bash
cp credentials.json.example credentials.json
# Edit with your actual API details
```

### 3. Test Your Setup
```bash
python3 test_api.py --provider api --model "fdtn-ai/Foundation-Sec-8B"
```

### 4. Run Analysis

**With credentials from file/environment:**
```bash
python3 reconftw_ai.py \
  --provider api \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir /path/to/reconftw_results \
  --report-type bughunter
```

**With direct credentials:**
```bash
python3 reconftw_ai.py \
  --provider api \
  --api-url "https://your-api-domain.com/v1/generate" \
  --api-username "your-username" \
  --api-password "your-password" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir /path/to/reconftw_results \
  --report-type bughunter
```

## 📋 What It Does

- **Analyzes ReconFTW outputs** from `osint/`, `subdomains/`, `hosts/`, `webs/` directories
- **Generates tailored reports** for different audiences (executives, pentesters, bug hunters)
- **Supports multiple LLM providers** (Ollama, custom APIs, Claude)
- **Customizable prompts** via JSON configuration
- **Concurrent processing** for faster analysis

## 🛠️ Installation

### Automatic Installation
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

**1. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**2. For Ollama (optional):**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3:8b
```

**3. Setup credentials:**
```bash
cp credentials.json.example credentials.json
# Edit with your API details
```

## 🔑 Credential Management

### Environment Variables (Recommended)
```bash
export API_URL="https://your-api-domain.com/v1/generate"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
export CLAUDE_API_KEY="sk-ant-your-claude-key"
```

### credentials.json File
```json
{
  "api_url": "https://your-api-domain.com/v1/generate",
  "api_username": "your-username",
  "api_password": "your-password",
  "claude_api_key": "sk-ant-your-claude-key"
}
```

**Credential Priority:** Command line arguments > Environment variables > credentials.json

This means you can override any credential by passing it directly in the command line, even if it's set in environment variables or credentials.json file.

## 🌐 Supported Providers

### 1. Custom API
Works with your curl example format:
```bash
python3 reconftw_ai.py \
  --provider api \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir ./reconftw_output
```

### 2. Claude API
High-quality analysis with Anthropic's models:
```bash
python3 reconftw_ai.py \
  --provider claude \
  --model "claude-3-sonnet-20240229" \
  --results-dir ./reconftw_output
```

### 3. Ollama (Local)
Free, private, no API limits:
```bash
python3 reconftw_ai.py \
  --provider ollama \
  --model "llama3:8b" \
  --results-dir ./reconftw_output
```

## 📊 Report Types

### Executive (`--report-type executive`)
**For CISOs and management**
- 200-400 word summaries
- Business impact focus
- Non-technical language
- Risk-based recommendations

### Brief (`--report-type brief`)
**Quick overview**
- Exactly 5 bullet points per category
- 1-2 sentences each
- Severity-ranked findings

### Bug Hunter (`--report-type bughunter`)
**For pentesters**
- 300-500 word technical analysis
- Attack paths and exploitation steps
- Prioritized vulnerability assessment

## 🔧 Usage Examples

### Basic Usage
```bash
python3 reconftw_ai.py \
  --provider api \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir ./reconftw_output \
  --report-type executive \
  --output-format md
```

### With Direct Credentials (No Config Files)
```bash
python3 reconftw_ai.py \
  --provider api \
  --api-url "https://your-api-domain.com/v1/generate" \
  --api-username "your-username" \
  --api-password "your-password" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir ./reconftw_output \
  --report-type bughunter
```

### With API Key Authentication
```bash
python3 reconftw_ai.py \
  --provider api \
  --api-url "https://your-api-domain.com/v1/generate" \
  --api-key "your-api-key" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir ./reconftw_output
```

### With Claude API
```bash
python3 reconftw_ai.py \
  --provider claude \
  --claude-api-key "sk-ant-your-key" \
  --model "claude-3-sonnet-20240229" \
  --results-dir ./reconftw_output
```

### With Custom Parameters
```bash
python3 reconftw_ai.py \
  --provider api \
  --api-url "https://your-api.com/v1/generate" \
  --api-username "user" \
  --api-password "pass" \
  --model "custom-model" \
  --max-tokens 1024 \
  --temperature 0.3 \
  --report-type executive
```

## ⚙️ Command Line Options

### Required
- `--provider`: LLM provider (`ollama`, `api`, `claude`)
- `--model`: Model name to use

### Optional
- `--results-dir`: ReconFTW results directory (default: `./reconftw_output`)
- `--output-dir`: Output directory (default: `./reconftw_ai_output`)
- `--report-type`: Report style (`executive`, `brief`, `bughunter`)
- `--output-format`: Output format (`txt`, `md`)
- `--max-tokens`: Maximum tokens for generation (default: 512)
- `--temperature`: Generation temperature 0.0-1.0 (default: 0.5)

### API Options
- `--api-url`: API endpoint URL
- `--api-username`: API username (for basic auth)
- `--api-password`: API password (for basic auth)
- `--api-key`: API key (for bearer token auth)
- `--api-headers`: Custom headers as JSON string

### Claude Options
- `--claude-api-key`: Claude API key

## 🧪 Testing

### Test API Connection
```bash
python3 test_api.py --provider api --model "fdtn-ai/Foundation-Sec-8B"
```

### Test Claude API
```bash
python3 test_api.py --provider claude --model "claude-3-sonnet-20240229"
```

### Test Ollama
```bash
python3 test_api.py --provider ollama --model "llama3:8b"
```

## 🔧 Troubleshooting

### Common Issues

**"API URL is required"**
- Set `API_URL` environment variable or add to credentials.json

**"No authentication credentials found"**
- Set username/password or API key via environment or credentials file

**"Connection error"**
- Check API URL and network connectivity
- Verify API endpoint is accessible

**"Invalid JSON response"**
- Check if API returns expected JSON format
- Verify authentication is working

### Debug Commands
```bash
# Test credential loading
python3 test_api.py --provider api

# Check what credentials are found
python3 reconftw_ai.py --provider api --model test 2>&1 | grep "Authentication"
```

## 🔒 Security

- Use environment variables for production
- Add `credentials.json` to `.gitignore`
- Never commit API keys to version control
- Use API keys instead of passwords when possible


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with various ReconFTW outputs
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.