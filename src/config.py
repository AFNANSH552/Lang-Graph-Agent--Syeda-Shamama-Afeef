from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

# Load .env explicitly
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if not os.path.exists(env_path):
    raise FileNotFoundError(f".env file not found at {env_path}")
load_dotenv(dotenv_path=env_path, override=True)

class Settings(BaseSettings):
    openai_api_key_1: str
    openai_api_key_2: str
    atlas_server_url: str = "http://localhost:8001"
    atlas_server_key: str = "your-atlas-server-key"
    common_server_url: str = "http://localhost:8002"
    common_server_key: str = "your-common-server-key"
    agent_name: str = "Langie"
    agent_version: str = "1.0.0"
    log_level: str = "INFO"
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

try:
    settings = Settings()
    print("✅ Settings loaded successfully!")
except Exception as e:
    print("❌ ERROR: Failed to load configuration.")
    print(e)
    exit(1)

def get_primary_api_key(): return settings.openai_api_key_1
def get_secondary_api_key(): return settings.openai_api_key_2
def get_atlas_config(): return {"url": settings.atlas_server_url, "key": settings.atlas_server_key}
def get_common_config(): return {"url": settings.common_server_url, "key": settings.common_server_key}
