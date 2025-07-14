# ReconFTW-AI

Integrate a local LLM or remote API with ReconFTW to interpret pentesting results by category. Supports both local Ollama models and remote LLM APIs with authentication.

## 🧠 What does it do?

It analyzes ReconFTW outputs (`osint/`, `subdomains/`, `hosts/`, `webs/`) and generates a report using either a local LLM via Ollama or a remote LLM API, classifying the results based on the type of audience: executive, brief summary, or offensive bug bounty style. Prompts are loaded dynamically from a `prompts.json` file for easy customization.

## 📦 Installation

### For Local Ollama Usage:

1. Install Ollama:
```bash
curl https://ollama.ai/install.sh | sh
```

2. Pull a model:
```bash
ollama pull llama3:8b  # or your preferred model
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### For API Usage:

Just install the dependencies:
```bash
pip install -r requirements.txt
```

4. Ensure the `prompts.json` file is present in the working directory (included in the repository) or provide a custom prompts file.

## 🧪 Usage

### Local Ollama Usage (Default):
```bash
python reconftw_ai.py \
  --results-dir /path/to/reconftw_results \
  --output-dir /path/to/output \
  --model llama3:8b \
  --output-format md \
  --report-type bughunter
```

### Remote API Usage:
```bash
python reconftw_ai.py \
  --results-dir /path/to/reconftw_results \
  --output-dir /path/to/output \
  --use-api \
  --api-url "https://your-api-domain.com/endpoint" \
  --api-username "your-username" \
  --api-password "your-password" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --max-tokens 512 \
  --temperature 0.5 \
  --output-format md \
  --report-type executive
```

### Arguments:
- `--results-dir`: Input directory with `osint/`, `subdomains/`, `hosts/`, `webs/` (default: `./reconftw_output`)
- `--output-dir`: Where to save the report (default: `./reconftw_ai_output`)
- `--model`: Model to use - Ollama model name for local, or API model name for remote (default: `llama3`)
- `--output-format`: Output format: `txt` or `md` (default: `txt`)
- `--report-type`: Report style: `executive`, `brief`, or `bughunter` (default: `executive`)
- `--prompts-file`: JSON file containing prompt templates (default: `prompts.json`)

#### API-specific arguments:
- `--use-api`: Use remote API instead of local Ollama
- `--api-url`: API endpoint URL (required when using `--use-api`)
- `--api-username`: API username for authentication (required when using `--use-api`)
- `--api-password`: API password for authentication (required when using `--use-api`)
- `--max-tokens`: Maximum tokens for API response (default: `512`)
- `--temperature`: Temperature for API generation (default: `0.5`)

### Example API Usage with Custom Parameters:
```bash
# For executive report with more tokens
python reconftw_ai.py \
  --results-dir ./reconftw_output \
  --use-api \
  --api-url "https://api.example.com/v1/completions" \
  --api-username "myuser" \
  --api-password "mypass" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --max-tokens 1024 \
  --temperature 0.7 \
  --report-type executive \
  --output-format md

# For brief summary with lower temperature (more focused)
python reconftw_ai.py \
  --results-dir ./reconftw_output \
  --use-api \
  --api-url "https://api.example.com/v1/completions" \
  --api-username "myuser" \
  --api-password "mypass" \
  --model "fdtn-ai/Foundation-Sec-8B" \
  --max-tokens 256 \
  --temperature 0.3 \
  --report-type brief
```

### Customizing Prompts
The `prompts.json` file defines the LLM prompts for each report type and category. You can modify it to tailor the output structure, tone, or focus. Example structure:
```json
{
  "executive": {
    "osint": "As a security analyst, create a 200-300 word executive summary...",
    ...
  },
  ...
}
```

## 🖥️ Minimum Hardware Requirements

### For Local Ollama:

#### CPU-Only (Minimal Setup)
- **RAM**: 8 GB (for quantized 2B–7B models)
- **Processor**: 4-core or better
- **Storage**: 5–10 GB

#### Recommended CPU Setup
- **RAM**: 16 GB or more (for LLaMA 3 8B / Mistral 7B)
- **Processor**: 8-core modern CPU
- **Storage**: 10–20 GB

#### GPU Setup (Recommended for Speed)
- **RAM**: 8–16 GB system RAM
- **VRAM**:
  - 4 GB: Small models (Gemma 2B)
  - 6–8 GB: LLaMA 3 8B (quantized)
  - 12 GB+: LLaMA 13B
- **GPU**: NVIDIA GPU with CUDA (GTX 1060+)

### For API Usage:
- Minimal requirements - just needs to run Python and make HTTP requests
- **RAM**: 4 GB
- **Processor**: Any modern CPU
- **Storage**: 1 GB (for ReconFTW results and reports)
- **Network**: Stable internet connection

### Notes
- Quantization (4-bit/8-bit) is highly recommended for local models to save memory
- SSD recommended if ReconFTW output is large
- Works on Linux, macOS, and WSL
- API usage is recommended for resource-constrained environments

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

When using the API mode:
- Credentials are sent via HTTP Basic Authentication
- Use HTTPS endpoints to ensure encrypted transmission
- Consider using environment variables for sensitive credentials:
  ```bash
  export API_USERNAME="your-username"
  export API_PASSWORD="your-password"
  
  python reconftw_ai.py \
    --use-api \
    --api-url "https://api.example.com/v1/completions" \
    --api-username "$API_USERNAME" \
    --api-password "$API_PASSWORD" \
    --model "fdtn-ai/Foundation-Sec-8B"
  ```

## 🤝 Contributions
Pull requests and issues are welcome! To contribute new prompts, update the `prompts.json` file and test with various ReconFTW outputs.