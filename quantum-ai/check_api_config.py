#!/usr/bin/env python3
"""Quick test of LLM provider configuration"""
import os
import json

print("=" * 70)
print("  🔑 API KEY CONFIGURATION CHECK")
print("=" * 70)

# Load local.settings.json
config_path = "/workspaces/AI/local.settings.json"
with open(config_path, 'r') as f:
    config = json.load(f)

values = config.get('Values', {})

print("\n📋 Current Configuration:\n")

# Check each provider
providers_found = []

# LMStudio
lmstudio_url = values.get('LMSTUDIO_BASE_URL', '')
if lmstudio_url:
    print(f"✓ LMStudio configured: {lmstudio_url}")
    providers_found.append('lmstudio')
else:
    print("○ LMStudio: Not configured")

# Azure OpenAI
azure_key = values.get('AZURE_OPENAI_API_KEY', '')
azure_endpoint = values.get('AZURE_OPENAI_ENDPOINT', '')
azure_deployment = values.get('AZURE_OPENAI_DEPLOYMENT', '')
if azure_key and azure_endpoint and azure_deployment:
    print(f"✓ Azure OpenAI configured")
    print(f"  Endpoint: {azure_endpoint}")
    print(f"  Deployment: {azure_deployment}")
    print(f"  Key: {'*' * len(azure_key[:8])}... (hidden)")
    providers_found.append('azure')
elif azure_key or azure_endpoint or azure_deployment:
    print("⚠ Azure OpenAI partially configured (missing some fields)")
else:
    print("○ Azure OpenAI: Not configured")

# OpenAI
openai_key = values.get('OPENAI_API_KEY', '')
if openai_key:
    print(f"✓ OpenAI configured")
    print(f"  Key: {'*' * len(openai_key[:8])}... (hidden)")
    providers_found.append('openai')
else:
    print("○ OpenAI: Not configured")

print("\n" + "=" * 70)

if providers_found:
    print(f"✅ {len(providers_found)} provider(s) configured: {', '.join(providers_found)}")
    print("\n🚀 Ready to test quantum-LLM integration!")
    print("\nRun: cd /workspaces/AI/quantum-ai && python quantum_llm_integration.py")
else:
    print("⚠️  No LLM providers configured")
    print("\n📝 To configure:\n")
    print("Option 1: LMStudio (Local, Free)")
    print('  1. Start LMStudio app')
    print('  2. Load a model (e.g., Llama, Mistral)')
    print('  3. Start server on http://localhost:1234')
    print('  4. Already configured in local.settings.json!')
    
    print("\nOption 2: Azure OpenAI")
    print('  1. Get API key from Azure Portal')
    print('  2. Edit local.settings.json:')
    print('     "AZURE_OPENAI_API_KEY": "your-key"')
    print('     "AZURE_OPENAI_ENDPOINT": "https://your-resource.openai.azure.com/"')
    print('     "AZURE_OPENAI_DEPLOYMENT": "gpt-4"')
    
    print("\nOption 3: OpenAI")
    print('  1. Get API key from platform.openai.com')
    print('  2. Edit local.settings.json:')
    print('     "OPENAI_API_KEY": "sk-proj-..."')

print("\n" + "=" * 70)
