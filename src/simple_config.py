"""
Simple Configuration - No complex dependencies
"""
import os

# API Keys from environment variables (your keys are in .env file)
def get_primary_api_key() -> str:
    """Get primary API key from environment or default"""
    return os.getenv("OPENAI_API_KEY_1", "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")

def get_secondary_api_key() -> str:
    """Get secondary API key from environment or default"""
    return os.getenv("OPENAI_API_KEY_2", "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")

# Agent settings
AGENT_NAME = "Langie"
AGENT_VERSION = "1.0.0"
MODEL_NAME = "gpt-4"
TEMPERATURE = 0.1
MAX_TOKENS = 2000

# Server configurations
ATLAS_SERVER_URL = "http://localhost:8001"
ATLAS_SERVER_KEY = "atlas-key"
COMMON_SERVER_URL = "http://localhost:8002" 
COMMON_SERVER_KEY = "common-key"

def get_atlas_config() -> dict:
    """Get Atlas server configuration"""
    return {
        "url": ATLAS_SERVER_URL,
        "key": ATLAS_SERVER_KEY
    }

def get_common_config() -> dict:
    """Get Common server configuration"""
    return {
        "url": COMMON_SERVER_URL,
        "key": COMMON_SERVER_KEY
    }
