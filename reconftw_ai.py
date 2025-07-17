#!/usr/bin/env python3

import ollama
import os
import argparse
import glob
import sys
import subprocess
import shutil
import json
import requests
from datetime import datetime
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid
import base64
import anthropic

# Default configuration
DEFAULT_RECONFTW_RESULTS_DIR = "./reconftw_output"
DEFAULT_OUTPUT_DIR = "./reconftw_ai_output"
DEFAULT_MODEL_NAME = "llama3"
DEFAULT_OUTPUT_FORMAT = "txt"
DEFAULT_REPORT_TYPE = "executive"
DEFAULT_PROMPTS_FILE = "prompts.json"

REPORT_TYPES = ["executive", "brief", "bughunter"]
OUTPUT_FORMATS = ["txt", "md"]
CATEGORIES = ["osint", "subdomains", "hosts", "webs"]
LLM_PROVIDERS = ["ollama", "api", "claude"]


def load_credentials():
    """Load credentials from environment variables and credentials.json"""
    credentials = {}

    # Load from environment variables
    env_creds = {
        'api_url': os.getenv('API_URL'),
        'api_username': os.getenv('API_USERNAME'),
        'api_password': os.getenv('API_PASSWORD'),
        'api_key': os.getenv('API_KEY'),
        'claude_api_key': os.getenv('CLAUDE_API_KEY')
    }

    # Add non-empty env vars
    for key, value in env_creds.items():
        if value:
            credentials[key] = value

    # Load from credentials.json if exists
    if os.path.exists('credentials.json'):
        try:
            with open('credentials.json', 'r') as f:
                file_creds = json.load(f)
                # Only add if not already in credentials (env vars take priority)
                for key, value in file_creds.items():
                    if key not in credentials and value:
                        credentials[key] = value
        except Exception as e:
            print(f"[WARNING] Error reading credentials.json: {e}")

    return credentials


def get_credential_value(credentials, *keys):
    """Get credential value by checking multiple possible key names"""
    for key in keys:
        if key in credentials and credentials[key]:
            return credentials[key]
    return None


class APIConfig:
    def __init__(self, api_url: str, username: str = None, password: str = None,
                 api_key: str = None, headers: Dict = None):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.api_key = api_key
        self.headers = headers or {}


class LLMProvider:
    def __init__(self, provider_type: str, model_name: str, config: APIConfig = None):
        self.provider_type = provider_type
        self.model_name = model_name
        self.config = config

        if provider_type == "claude":
            if not config or not config.api_key:
                raise ValueError("Claude API requires an API key")
            self.client = anthropic.Anthropic(api_key=config.api_key)

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.5) -> str:
        if self.provider_type == "ollama":
            return self._generate_ollama(prompt)
        elif self.provider_type == "api":
            return self._generate_api(prompt, max_tokens, temperature)
        elif self.provider_type == "claude":
            return self._generate_claude(prompt, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {self.provider_type}")

    def _generate_ollama(self, prompt: str) -> str:
        try:
            response = ollama.generate(model=self.model_name, prompt=prompt)
            return response.get("response", "[Error] Empty response from model.")
        except Exception as e:
            return f"[Error] Ollama generation failed: {str(e)}"

    def _generate_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            headers = {
                "Content-Type": "application/json",
                **self.config.headers
            }

            # Prepare authentication
            auth = None
            if self.config.username and self.config.password:
                auth = (self.config.username, self.config.password)
            elif self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"

            data = {
                "model": self.model_name,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }

            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=data,
                auth=auth,
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            # Handle different response formats
            if "response" in result:
                return result["response"]
            elif "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0].get("text", "")
            elif "content" in result:
                return result["content"]
            else:
                return str(result)

        except requests.exceptions.RequestException as e:
            return f"[Error] API request failed: {str(e)}"
        except json.JSONDecodeError as e:
            return f"[Error] Invalid JSON response: {str(e)}"
        except Exception as e:
            return f"[Error] API generation failed: {str(e)}"

    def _generate_claude(self, prompt: str, max_tokens: int, temperature: float) -> str:
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            return f"[Error] Claude API generation failed: {str(e)}"


def load_prompts(prompts_file: str) -> Dict:
    try:
        with open(prompts_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Prompts file '{prompts_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in prompts file: {e}")
        sys.exit(1)


def ensure_ollama_running():
    try:
        subprocess.run(["ollama", "list"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print("[!] Ollama is not running. Attempting to start it in background...")
        if shutil.which("ollama") is None:
            print("[ERROR] Ollama not installed or not in PATH.")
            sys.exit(1)
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ensure_model_available(model_name):
    try:
        output = subprocess.check_output(["ollama", "list"], encoding="utf-8")
        if model_name not in output:
            print(f"[*] Model '{model_name}' not found. Downloading with 'ollama pull {model_name}'...")
            subprocess.run(["ollama", "pull", model_name], check=True)
    except Exception as e:
        print(f"[ERROR] Could not verify or pull model: {e}")
        sys.exit(1)


def setup_llm_provider(args: argparse.Namespace) -> LLMProvider:
    # Load credentials
    credentials = load_credentials()

    if args.provider == "ollama":
        ensure_ollama_running()
        ensure_model_available(args.model)
        return LLMProvider("ollama", args.model)

    elif args.provider == "api":
        # Get API URL - priority: args > credentials > error
        api_url = args.api_url or get_credential_value(credentials, 'api_url', 'url')
        if not api_url:
            print("[ERROR] API URL is required for API provider")
            print("Set via --api-url argument or API_URL environment variable")
            print("Or add to credentials.json: {\"api_url\": \"https://your-api.com\"}")
            sys.exit(1)

        # Get authentication - priority: args > credentials
        username = args.api_username or get_credential_value(credentials, 'api_username', 'username')
        password = args.api_password or get_credential_value(credentials, 'api_password', 'password')
        api_key = args.api_key or get_credential_value(credentials, 'api_key', 'key')

        # Parse headers
        headers = {}
        if args.api_headers:
            try:
                headers = json.loads(args.api_headers)
            except json.JSONDecodeError:
                print("[ERROR] Invalid JSON format for API headers")
                sys.exit(1)
        elif 'headers' in credentials:
            headers = credentials['headers']

        # Check if we have authentication
        if not (username and password) and not api_key:
            print("[WARNING] No authentication credentials found for API")

        config = APIConfig(
            api_url=api_url,
            username=username,
            password=password,
            api_key=api_key,
            headers=headers
        )

        print(f"[*] Using API: {api_url}")
        if username:
            print(f"[*] Authentication: Basic auth (user: {username})")
        elif api_key:
            print(f"[*] Authentication: Bearer token")

        return LLMProvider("api", args.model, config)

    elif args.provider == "claude":
        # Get Claude API key - priority: args > credentials > error
        claude_key = args.claude_api_key or get_credential_value(credentials, 'claude_api_key', 'claude_key')
        if not claude_key:
            print("[ERROR] Claude API key is required for Claude provider")
            print("Set via --claude-api-key argument or CLAUDE_API_KEY environment variable")
            print("Or add to credentials.json: {\"claude_api_key\": \"sk-ant-...\"}")
            sys.exit(1)

        config = APIConfig(
            api_url="https://api.anthropic.com/v1/messages",
            api_key=claude_key
        )

        print(f"[*] Using Claude API with model: {args.model}")
        return LLMProvider("claude", args.model, config)

    else:
        print(f"[ERROR] Unsupported provider: {args.provider}")
        sys.exit(1)


def read_files(category: str, results_dir: str) -> str:
    combined_data = ""
    category_dir = os.path.join(results_dir, category)

    if not os.path.isdir(category_dir):
        return f"[Error] Directory {category_dir} does not exist."

    file_paths = glob.glob(os.path.join(category_dir, "**/*"), recursive=True)

    for file_path in file_paths:
        if os.path.isfile(file_path):
            relative_path = os.path.relpath(file_path, results_dir)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_data += f"--- {relative_path} ---\n{f.read().strip()}\n"
            except Exception as e:
                combined_data += f"[Error] Failed to read {relative_path}: {str(e)}\n"

    if not combined_data:
        return f"[Info] No files found in {category_dir}."

    return combined_data.strip()


def process_category(category: str, data: str, llm_provider: LLMProvider,
                     report_type: str, base_prompts: Dict, max_tokens: int = 512,
                     temperature: float = 0.5) -> str:
    if not data:
        return f"[Error] No data available for {category}."

    prompt_template = base_prompts.get(report_type, {}).get(category, "Analyze this data:\n{data}")
    prompt = prompt_template.format(data=data)

    try:
        return llm_provider.generate(prompt, max_tokens, temperature)
    except Exception as e:
        return f"[Error] Failed to process {category}: {str(e)}"


def save_results(results: Dict[str, str], output_dir: str, model_name: str,
                 output_format: str, report_type: str, provider: str):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = "md" if output_format == "md" else "txt"
    output_file = os.path.join(output_dir, f"reconftw_analysis_{report_type}_{timestamp}.{extension}")

    with open(output_file, "w", encoding="utf-8") as f:
        if output_format == "md":
            f.write(f"# ReconFTW-AI Analysis\n\n")
            f.write(f"- **Provider**: `{provider}`\n")
            f.write(f"- **Model Used**: `{model_name}`\n")
            f.write(f"- **Report Type**: `{report_type}`\n")
            f.write(f"- **Date**: `{timestamp}`\n\n")
            for category, interpretation in results.items():
                f.write(f"## {category.upper()}\n\n{interpretation}\n\n")
        else:
            f.write(
                f"ReconFTW-AI Analysis\nProvider: {provider}\nModel: {model_name}\nReport Type: {report_type}\nDate: {timestamp}\n")
            f.write("=" * 60 + "\n\n")
            for category, interpretation in results.items():
                f.write(f"=== {category.upper()} ===\n{interpretation}\n\n")

    print(f"[*] Results saved to '{output_file}'")


def analyze_reconftw_results(results_dir: str, llm_provider: LLMProvider,
                             report_type: str, base_prompts: Dict, max_tokens: int = 512,
                             temperature: float = 0.5) -> Dict[str, str]:
    results = {}
    all_data = ""

    # Read all files first
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(read_files, category, results_dir): category
            for category in CATEGORIES
        }

        raw_data_per_category = {}
        for future in as_completed(futures):
            category = futures[future]
            raw_data = future.result()
            raw_data_per_category[category] = raw_data

    # Process with LLM
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(process_category, category, raw_data_per_category[category],
                            llm_provider, report_type, base_prompts, max_tokens, temperature): category
            for category in CATEGORIES
        }

        for future in as_completed(futures):
            category = futures[future]
            interpretation = future.result()
            results[category] = interpretation
            all_data += f"{category.upper()}:\n{raw_data_per_category[category]}\n\n"

    # Generate overview
    results["overview"] = process_category("overview", all_data, llm_provider,
                                           report_type, base_prompts, max_tokens, temperature)
    return results


def validate_args(args: argparse.Namespace, parser: argparse.ArgumentParser) -> bool:
    if not os.path.isdir(args.results_dir):
        print(f"[Error] Results directory '{args.results_dir}' does not exist.")
        parser.print_help()
        return False
    if args.output_format not in OUTPUT_FORMATS:
        print(f"[Error] Invalid format '{args.output_format}'. Choose from: {', '.join(OUTPUT_FORMATS)}")
        return False
    if args.report_type not in REPORT_TYPES:
        print(f"[Error] Invalid report type '{args.report_type}'. Choose from: {', '.join(REPORT_TYPES)}")
        return False
    if args.provider not in LLM_PROVIDERS:
        print(f"[Error] Invalid provider '{args.provider}'. Choose from: {', '.join(LLM_PROVIDERS)}")
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="ReconFTW-AI: Use LLMs to interpret ReconFTW results")

    # Basic arguments
    parser.add_argument("--results-dir", default=DEFAULT_RECONFTW_RESULTS_DIR,
                        help="Directory with ReconFTW results.")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR,
                        help="Where to save the analysis.")
    parser.add_argument("--model", default=DEFAULT_MODEL_NAME,
                        help="Model name to use.")
    parser.add_argument("--output-format", choices=OUTPUT_FORMATS,
                        default=DEFAULT_OUTPUT_FORMAT, help="Output format: txt or md.")
    parser.add_argument("--report-type", choices=REPORT_TYPES,
                        default=DEFAULT_REPORT_TYPE, help="Type of report to generate.")
    parser.add_argument("--prompts-file", default=DEFAULT_PROMPTS_FILE,
                        help="JSON file containing prompt templates.")

    # LLM Provider arguments
    parser.add_argument("--provider", choices=LLM_PROVIDERS, default="ollama",
                        help="LLM provider to use: ollama, api, or claude")

    # API arguments
    parser.add_argument("--api-url", help="API endpoint URL (for API provider)")
    parser.add_argument("--api-username", help="API username (for basic auth)")
    parser.add_argument("--api-password", help="API password (for basic auth)")
    parser.add_argument("--api-key", help="API key (for bearer token auth)")
    parser.add_argument("--api-headers", help="Additional headers as JSON string")

    # Claude API arguments
    parser.add_argument("--claude-api-key", help="Claude API key")

    # Generation parameters
    parser.add_argument("--max-tokens", type=int, default=512,
                        help="Maximum tokens for generation")
    parser.add_argument("--temperature", type=float, default=0.5,
                        help="Temperature for generation (0.0-1.0)")

    args = parser.parse_args()

    if not validate_args(args, parser):
        sys.exit(1)

    base_prompts = load_prompts(args.prompts_file)
    llm_provider = setup_llm_provider(args)

    print(
        f"[*] Analyzing with {args.provider} provider using model '{args.model}' and report type '{args.report_type}'...")
    results = analyze_reconftw_results(args.results_dir, llm_provider, args.report_type,
                                       base_prompts, args.max_tokens, args.temperature)

    for category, content in results.items():
        print(f"\n=== {category.upper()} ===\n{content[:500]}{'...' if len(content) > 500 else ''}")

    save_results(results, args.output_dir, args.model, args.output_format,
                 args.report_type, args.provider)


if __name__ == "__main__":
    main()