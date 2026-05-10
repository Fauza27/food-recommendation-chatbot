"""
Configuration loader for Food Chatbot Pipeline
Loads environment variables from .env file
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Azure Speech Service Configuration
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY")
AZURE_REGION = os.getenv("AZURE_REGION", "southeastasia")

# OpenAI API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# GCP Maps API Configuration
GCP_MAPS_API_KEY = os.getenv("GCP_MAPS_API_KEY")

# Model Configuration
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))

def check_azure_credentials():
    """Check if Azure credentials are set."""
    if not AZURE_SPEECH_KEY:
        print("[ERROR] AZURE_SPEECH_KEY tidak ditemukan!")
        print("Silakan:")
        print("1. Copy .env.example menjadi .env")
        print("2. Isi AZURE_SPEECH_KEY dengan key Anda")
        print("3. Isi AZURE_REGION dengan region Anda")
        return False
    return True

def check_openai_credentials():
    """Check if OpenAI credentials are set."""
    if not OPENAI_API_KEY:
        print("[ERROR] OPENAI_API_KEY tidak ditemukan!")
        print("Silakan:")
        print("1. Copy .env.example menjadi .env")
        print("2. Isi OPENAI_API_KEY dengan key Anda")
        return False
    return True

def check_gcp_credentials():
    """Check if GCP Maps credentials are set."""
    if not GCP_MAPS_API_KEY:
        print("[ERROR] GCP_MAPS_API_KEY tidak ditemukan!")
        print("Silakan:")
        print("1. Copy .env.example menjadi .env")
        print("2. Isi GCP_MAPS_API_KEY dengan key Anda")
        return False
    return True

def print_config_info():
    """Print configuration info (without showing actual keys)."""
    print("Configuration:")
    print(f"  Azure Region: {AZURE_REGION}")
    print(f"  Azure Key: {'[SET]' if AZURE_SPEECH_KEY else '[NOT SET]'}")
    print(f"  OpenAI Key: {'[SET]' if OPENAI_API_KEY else '[NOT SET]'}")
    print(f"  GCP Maps Key: {'[SET]' if GCP_MAPS_API_KEY else '[NOT SET]'}")
    print(f"  OpenAI Model: {OPENAI_MODEL}")
    print(f"  Temperature: {OPENAI_TEMPERATURE}")
    print(f"  Max Tokens: {OPENAI_MAX_TOKENS}")
