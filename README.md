## 🔑 Credential Management

ReconFTW-AI supports two simple ways to manage credentials:

### Method 1: Environment Variables (Recommended)
```bash
export API_URL="https://your-api-domain.com/v1/generate"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
export CLAUDE_API_KEY="sk-ant-your-claude-key"
```

### Method 2: credentials.json File
Create a `credentials.json` file in your project directory:
```json
{
  "api_url": "https://your-api-domain.com/v1/generate",
  "api_username": "your-username",
  "api# ReconFTW-AI

Integrate a local LLM or API-based LLM with ReconFTW to interpret pentesting results by category. Now supports multiple LLM providers including Ollama, custom APIs, and Claude API.

## 🧠 What does it do?

It analyzes ReconFTW outputs (`osint/`, `subdomains/`, `hosts/`, `webs/`) and generates a report using various LLM providers, classifying the results based on the type of audience: executive, brief summary, or offensive bug bounty style. Prompts are loaded dynamically from a `prompts.json` file for easy customization.

## 📦 Installation

### For Ollama (Local LLM)
1. Install Ollama:
```bash
curl https://ollama.ai/install.sh | sh
```

2. Pull a model:
```bash
ollama pull llama3:8b  # or your preferred model
```

### For API/Claude Support
3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure the `prompts.json` file is present in the working directory (included in the repository) or provide a custom prompts file.

## 🚀 Quick Start

### 1. Setup Credentials
Choose one of two methods:

**Method A: Environment Variables (Recommended)**
```bash
export API_URL="https://your-api-domain.com/v1/generate"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
export CLAUDE_API_KEY="sk-ant-your-claude-key"
```

**Method B: credentials.json File**
```bash
# Copy example file
cp credentials.json.example credentials.json

# Edit with your actual values
{
  "api_url": "https://your-api-domain.com/v1/generate",
  "api_username": "your-username",
  "api_password": "your-password",
  "claude_api_key": "sk-ant-your-claude-key"
}
```

### 2. Test Your Setup
```bash
# Test custom API
python3 test_api.py --provider api --model "fdtn-ai/Foundation-Sec-8B"

# Test Claude API
python3 test_api.py --provider claude --model "claude-3-sonnet-20240229"

# Test Ollama
python3 test_api.py --provider ollama --model "llama3:8b"
```

### 3. Run Analysis
```bash
# With custom API
python3 reconftw_ai.py \
  --provider api \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir /path/to/reconftw_results \
  --report-type bughunter

# With Claude API
python3 reconftw_ai.py \
  --provider claude \
  --model "claude-3-sonnet-20240229" \
  --results-dir /path/to/reconftw_results \
  --report-type executive
```

### Basic Usage with Ollama (Local)
```bash
python reconftw_ai.py \
  --results-dir /path/to/reconftw_results \
  --output-dir /path/to/output \
  --provider ollama \
  --model llama3:8b \
  --output-format md \
  --report-type bughunter
```

### Usage with Custom API
```bash
python reconftw_ai.py \
  --results-dir /path/to/reconftw_results \
  --output-dir /path/to/output \
  --provider api \
  --api-url "https://your-api-domain.com/v1/generate" \
  --api-username "your-username" \
  --api-password "your-password" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --max-tokens 512 \
  --temperature 0.5 \
  --report-type executive
```

### Usage with API Key Authentication
```bash
python reconftw_ai.py \
  --results-dir /path/to/reconftw_results \
  --output-dir /path/to/output \
  --provider api \
  --api-url "https://your-api-domain.com/v1/generate" \
  --api-key "your-api-key" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --max-tokens 512 \
  --temperature 0.5 \
  --report-type brief
```

### Usage with Claude API
```bash
python reconftw_ai.py \
  --results-dir /path/to/reconftw_results \
  --output-dir /path/to/output \
  --provider claude \
  --claude-api-key "your-claude-api-key" \
  --model "claude-3-sonnet-20240229" \
  --max-tokens 1024 \
  --temperature 0.3 \
  --report-type bughunter
```

### Usage with Credentials File
```bash
# Create credentials.json with your API details
python reconftw_ai.py \
  --provider api \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir /path/to/reconftw_results \
  --report-type executive
```

### Usage with Environment Variables
```bash
# Set credentials
export API_URL="https://your-api.com/v1/generate"
export API_USERNAME="username"
export API_PASSWORD="password"

# Run analysis
python reconftw_ai.py \
  --provider api \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --results-dir /path/to/reconftw_results \
  --report-type bughunter
```

## 🔧 Arguments

### Basic Arguments
- `--results-dir`: Input directory with `osint/`, `subdomains/`, `hosts/`, `webs/` (default: `./reconftw_output`)
- `--output-dir`: Where to save the report (default: `./reconftw_ai_output`)
- `--model`: Model name to use (depends on provider)
- `--output-format`: Output format: `txt` or `md` (default: `txt`)
- `--report-type`: Report style: `executive`, `brief`, or `bughunter` (default: `executive`)
- `--prompts-file`: JSON file containing prompt templates (default: `prompts.json`)

### Provider Arguments
- `--provider`: LLM provider to use: `ollama`, `api`, or `claude` (default: `ollama`)

### API Provider Arguments
- `--api-url`: API endpoint URL (required for API provider)
- `--api-username`: API username (for basic authentication)
- `--api-password`: API password (for basic authentication)
- `--api-key`: API key (for bearer token authentication)
- `--api-headers`: Additional headers as JSON string

### Claude API Arguments
- `--claude-api-key`: Claude API key (required for Claude provider)

### Generation Parameters
- `--max-tokens`: Maximum tokens for generation (default: 512)
- `--temperature`: Temperature for generation, 0.0-1.0 (default: 0.5)

## 🌐 Supported LLM Providers

### 1. Ollama (Local)
- **Pros**: Free, private, no API limits
- **Cons**: Requires local resources
- **Setup**: Install Ollama and pull models locally
- **Models**: llama3, mistral, deepseek-r1, qwen2.5-coder, etc.

### 2. Custom API
- **Pros**: Scalable, cloud-based, various models
- **Cons**: Requires API access and may have costs
- **Authentication**: Supports both basic auth (username/password) and bearer token (API key)
- **Custom Headers**: Support for additional headers
- **Response Formats**: Handles various API response formats

### 3. Claude API
- **Pros**: High-quality responses, advanced reasoning
- **Cons**: Requires Anthropic API key and has usage costs
- **Models**: claude-3-sonnet-20240229, claude-3-opus-20240229, claude-3-haiku-20240307
- **Setup**: Get API key from Anthropic Console

## 🔑 Credential Management

ReconFTW-AI supports two simple ways to manage credentials:

### Method 1: Environment Variables (Recommended)
```bash
export API_URL="https://your-api-domain.com/v1/generate"
export API_USERNAME="your-username"
export API_PASSWORD="your-password"
export CLAUDE_API_KEY="sk-ant-your-claude-key"
```

### Method 2: credentials.json File
Create a `credentials.json` file in your project directory:
```json
{
  "api_url": "https://your-api-domain.com/v1/generate",
  "api_username": "your-username",
  "api_password": "your-password",
  "claude_api_key": "sk-ant-your-claude-key",
  "headers": {
    "User-Agent": "ReconFTW-AI/1.0"
  }
}
```

**Priority Order:** Command line arguments > Environment variables > credentials.json file

## 📊 Response Format Handling

The tool automatically handles various API response formats:
- OpenAI-style responses with `choices` array
- Simple responses with `response` field
- Direct content responses
- Custom API formats

## 🛠️ Customizing Prompts

The `prompts.json` file defines the LLM prompts for each report type and category. You can modify it to tailor the output structure, tone, or focus. Example structure:

```json
{
  "executive": {
    "osint": "As a security analyst, create a 200-300 word executive summary...",
    "subdomains": "Summarize the subdomain findings...",
    ...
  },
  "brief": {
    "osint": "Analyze the OSINT data and list exactly 5 key findings...",
    ...
  },
  "bughunter": {
    "osint": "As a bug bounty hunter, analyze the OSINT data...",
    ...
  }
}
```

## 🖥️ Minimum Hardware Requirements

### For Ollama (Local)
- **RAM**: 8-16 GB (depends on model size)
- **CPU**: 4-8 cores recommended
- **Storage**: 5-20 GB (for models)

### For API Providers
- **RAM**: 2-4 GB (minimal local processing)
- **CPU**: Any modern CPU
- **Network**: Stable internet connection

## ✅ Supported ReconFTW Categories
- `osint/`: leaks, credentials, GitHub, spoofing, etc.
- `subdomains/`: DNS, takeovers, bruteforce, cloud
- `hosts/`: IPs, ports, WAFs, vulnerabilities
- `webs/`: CMS, endpoints, JS, fuzzing, parameters
- `overview`: Global summary across all categories

## 📊 Report Types

### `--report-type executive`
> Tailored for CISOs, managers, and non-technical stakeholders. Provides 200-400 word summaries with 3-7 bullet points per category, focusing on business risks (e.g., financial, reputational).

### `--report-type brief`
> A compact summary with exactly 5 bullet points per category, each 1-2 sentences, ranked by severity.

### `--report-type bughunter`
> Offensive-style output for pentesters or bug bounty hunters, with 300-500 word responses and 3-7 prioritized attack paths per category.

## 🔒 Security Considerations

- **API Keys**: Never commit API keys to version control
- **Local Processing**: Use Ollama for sensitive data that shouldn't leave your network
- **Rate Limits**: Be aware of API rate limits and costs
- **Data Privacy**: Consider data privacy when using cloud-based APIs

## 🔧 Troubleshooting

### Common Issues

**"API URL is required"**
- Set `API_URL` environment variable or add `api_url` to credentials.json

**"No authentication credentials found"**
- Set username/password or API key via environment variables or credentials.json

**"Connection error"**
- Check your API URL and network connection
- Verify the API endpoint is accessible

**"Invalid JSON response"**
- Check if your API returns expected JSON format
- Verify API authentication is working

**"Claude API key is required"**
- Set `CLAUDE_API_KEY` environment variable or add to credentials.json

### Check Credential Loading
```bash
# Test what credentials are found
python3 test_api.py --provider api
```

### Security Tips
- Use environment variables for production deployments
- Add `credentials.json` to `.gitignore`
- Never commit API keys to version control
- Use API keys instead of passwords when possible

## 🤝 Contributions

Pull requests and issues are welcome! To contribute:
1. Fork the repository
2. Create a feature branch
3. Test with various ReconFTW outputs and LLM providers
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.