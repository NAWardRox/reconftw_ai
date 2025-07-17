#!/usr/bin/env python3

import requests
import json
import argparse
import sys
import anthropic
import os
from datetime import datetime


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


def get_credential(credentials, *keys):
    """Get credential value by checking multiple possible key names"""
    for key in keys:
        if key in credentials and credentials[key]:
            return credentials[key]
    return None


def test_custom_api(api_url, model, username=None, password=None, api_key=None, headers=None):
    """Test custom API endpoint"""
    print(f"[*] Testing Custom API: {api_url}")

    try:
        request_headers = {
            "Content-Type": "application/json",
            **(headers or {})
        }

        auth = None
        if username and password:
            auth = (username, password)
            print(f"[*] Using basic authentication")
        elif api_key:
            request_headers["Authorization"] = f"Bearer {api_key}"
            print(f"[*] Using bearer token authentication")

        test_data = {
            "model": model,
            "prompt": "What is SQL Injection? Provide a brief explanation.",
            "max_tokens": 100,
            "temperature": 0.5
        }

        print(f"[*] Request payload: {json.dumps(test_data, indent=2)}")

        response = requests.post(
            api_url,
            headers=request_headers,
            json=test_data,
            auth=auth,
            timeout=30
        )

        print(f"[*] Response status: {response.status_code}")
        print(f"[*] Response headers: {dict(response.headers)}")

        if response.status_code == 200:
            result = response.json()
            print(f"[✓] API test successful!")
            print(f"[*] Response: {json.dumps(result, indent=2)}")

            # Try to extract response content
            if "response" in result:
                print(f"[*] Generated text: {result['response'][:200]}...")
            elif "choices" in result and len(result["choices"]) > 0:
                print(f"[*] Generated text: {result['choices'][0].get('text', '')[:200]}...")
            elif "content" in result:
                print(f"[*] Generated text: {result['content'][:200]}...")

        else:
            print(f"[✗] API test failed!")
            print(f"[*] Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print(f"[✗] Connection error: Cannot connect to {api_url}")
    except requests.exceptions.Timeout:
        print(f"[✗] Timeout error: Request took too long")
    except json.JSONDecodeError as e:
        print(f"[✗] JSON decode error: {e}")
    except Exception as e:
        print(f"[✗] Unexpected error: {e}")


def test_claude_api(api_key, model):
    """Test Claude API"""
    print(f"[*] Testing Claude API with model: {model}")

    try:
        client = anthropic.Anthropic(api_key=api_key)

        response = client.messages.create(
            model=model,
            max_tokens=100,
            temperature=0.5,
            messages=[
                {"role": "user", "content": "What is SQL Injection? Provide a brief explanation."}
            ]
        )

        print(f"[✓] Claude API test successful!")
        print(f"[*] Response: {response.content[0].text[:200]}...")
        print(f"[*] Usage: {response.usage}")

    except anthropic.AuthenticationError:
        print(f"[✗] Authentication error: Invalid API key")
    except anthropic.RateLimitError:
        print(f"[✗] Rate limit error: Too many requests")
    except anthropic.APIError as e:
        print(f"[✗] API error: {e}")
    except Exception as e:
        print(f"[✗] Unexpected error: {e}")


def test_ollama(model):
    """Test Ollama local installation"""
    print(f"[*] Testing Ollama with model: {model}")

    try:
        import ollama

        response = ollama.generate(
            model=model,
            prompt="What is SQL Injection? Provide a brief explanation."
        )

        print(f"[✓] Ollama test successful!")
        print(f"[*] Response: {response.get('response', '')[:200]}...")

    except ImportError:
        print(f"[✗] Ollama library not installed. Run: pip install ollama")
    except Exception as e:
        print(f"[✗] Ollama error: {e}")
        print(f"[*] Make sure Ollama is running and model '{model}' is available")


def main():
    parser = argparse.ArgumentParser(description="Test LLM API endpoints for ReconFTW-AI")

    parser.add_argument("--provider", choices=["api", "claude", "ollama"], required=True,
                        help="Provider to test")
    parser.add_argument("--model", help="Model name to test")

    # API arguments
    parser.add_argument("--api-url", help="API endpoint URL")
    parser.add_argument("--api-username", help="API username")
    parser.add_argument("--api-password", help="API password")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--api-headers", help="Additional headers as JSON")

    # Claude arguments
    parser.add_argument("--claude-api-key", help="Claude API key")

    args = parser.parse_args()

    # Load credentials
    credentials = load_credentials()

    print(f"🧪 ReconFTW-AI API Tester")
    print(f"Provider: {args.provider}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    if args.provider == "api":
        # Get values with priority: args > credentials
        api_url = args.api_url or get_credential(credentials, 'api_url', 'url')
        username = args.api_username or get_credential(credentials, 'api_username', 'username')
        password = args.api_password or get_credential(credentials, 'api_password', 'password')
        api_key = args.api_key or get_credential(credentials, 'api_key', 'key')
        model = args.model or "fdtn-ai/Foundation-Sec-8B"

        if not api_url:
            print("[✗] API URL is required for API provider")
            print("Set via --api-url argument or API_URL environment variable")
            print("Or add to credentials.json: {\"api_url\": \"https://your-api.com\"}")
            sys.exit(1)

        headers = {}
        if args.api_headers:
            try:
                headers = json.loads(args.api_headers)
            except json.JSONDecodeError:
                print("[✗] Invalid JSON format for headers")
                sys.exit(1)
        elif 'headers' in credentials:
            headers = credentials['headers']

        print(f"Model: {model}")
        test_custom_api(api_url, model, username, password, api_key, headers)

    elif args.provider == "claude":
        claude_key = args.claude_api_key or get_credential(credentials, 'claude_api_key', 'claude_key')
        model = args.model or "claude-3-sonnet-20240229"

        if not claude_key:
            print("[✗] Claude API key is required")
            print("Set via --claude-api-key argument or CLAUDE_API_KEY environment variable")
            print("Or add to credentials.json: {\"claude_api_key\": \"sk-ant-...\"}")
            sys.exit(1)

        print(f"Model: {model}")
        test_claude_api(claude_key, model)

    elif args.provider == "ollama":
        model = args.model or "llama3:8b"
        print(f"Model: {model}")
        test_ollama(model)


if __name__ == "__main__":
    main()